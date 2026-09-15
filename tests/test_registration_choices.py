"""Conta, preferências e matrículas: integridade e efeitos no portal."""
import json
import unittest
from datetime import datetime
from unittest.mock import patch
from sqlalchemy.exc import SQLAlchemyError
import test_app as base
from app import (app, db, User, Plan, Location, ClassGroup, ClassEnrollment,
                 ClassPreference, ContractAcceptance, Attendance, personal_calendar_ics)


class RegistrationChoicesTests(unittest.TestCase):
    csrf = base.BJSportsTestCase.csrf
    login = base.BJSportsTestCase.login
    registration_payload = base.BJSportsTestCase.registration_payload

    def setUp(self):
        base.BJSportsTestCase.setUp(self)
        with app.app_context():
            plan = Plan.query.one()
            plan.name, plan.modality = 'Boxe', 'Boxe'
            db.session.add(Location(slug='teste', name='Unidade Teste', city='Teste', address='Teste', active=True))
            self.ids = []
            for index, modality in enumerate(('Boxe', 'Boxe', 'Jiu-Jitsu', 'MMA')):
                group = ClassGroup(name=f'Turma {index}', modality=modality, location_slug='teste',
                                   capacity=2, status='ativa', publish_public=True, audience='Adulto')
                group.schedules = ['Seg, Ter, Qua, Qui, Sex, Sáb, Dom • 06:30 e 19:00']
                db.session.add(group)
                db.session.flush()
                self.ids.append(group.id)
            db.session.commit()

    def register(self, ids=None, **overrides):
        data = self.registration_payload(regClassSelection=json.dumps(ids or []), **overrides)
        return self.client.post('/login', data={**data, 'csrf_token': self.csrf()}, follow_redirects=True)

    def fixed_plan(self, modalities='Boxe'):
        with app.app_context():
            plan = Plan.query.one()
            plan.name, plan.category, plan.modality = 'Plano fixo', 'Combos', modalities
            plan.force_all_days = False
            plan.selection_count = 2 if ',' in modalities else 0
            db.session.commit()

    def assert_no_partial_account(self):
        with app.app_context():
            self.assertIsNone(User.query.filter_by(username='novoaluno').first())
            self.assertEqual(ClassPreference.query.count(), 0)
            self.assertEqual(ClassEnrollment.query.count(), 0)

    def test_multiple_credit_preferences_are_not_seats_or_contract_acceptance(self):
        self.register(self.ids[:2])
        with app.app_context():
            user = User.query.filter_by(username='novoaluno').one()
            self.assertEqual(len(user.class_preferences), 2)
            self.assertEqual(ClassEnrollment.query.count(), 0)
            self.assertEqual(db.session.get(ClassGroup, self.ids[0]).enrolled, 0)
            self.assertEqual(ContractAcceptance.query.count(), 0)
            self.assertIsNone(user.membership_terms_accepted_at)
            self.assertAlmostEqual((user.contract_due_at-user.created_at).total_seconds(), 216000, delta=2)

    def test_empty_selection_keeps_account_pending(self):
        self.fixed_plan()
        page = self.register().get_data(as_text=True)
        self.assertIn('Escolha pendente', page)
        with app.app_context():
            self.assertIsNotNone(User.query.filter_by(username='novoaluno').first())
            self.assertEqual(ClassEnrollment.query.count(), 0)

    def test_full_group_accepts_preference_but_rejects_fixed_enrollment(self):
        with app.app_context():
            db.session.get(ClassGroup, self.ids[0]).capacity = 0
            db.session.commit()
        self.fixed_plan()
        self.assertIn('última vaga', self.register([self.ids[0]]).get_data(as_text=True))
        self.assert_no_partial_account()
        with app.app_context():
            plan = Plan.query.one()
            plan.category, plan.name = 'Planos Individuais', 'Boxe'
            db.session.commit()
        self.register([self.ids[0]])
        with app.app_context():
            self.assertEqual(ClassPreference.query.count(), 1)

    def test_fixed_combo_saves_one_enrollment_per_selected_modality(self):
        self.fixed_plan('Boxe, Jiu-Jitsu')
        self.register([self.ids[0], self.ids[2]], comboModalities=['Boxe', 'Jiu-Jitsu'])
        with app.app_context():
            self.assertEqual(ClassEnrollment.query.count(), 2)
            self.assertEqual(ClassPreference.query.count(), 0)
            self.assertEqual(db.session.get(ClassGroup, self.ids[0]).enrolled, 1)

    def test_duplicate_modality_or_invalid_combo_rolls_back_every_link(self):
        self.fixed_plan('Boxe, Jiu-Jitsu')
        self.register(self.ids[:2], comboModalities=['Boxe', 'Jiu-Jitsu'])
        self.assert_no_partial_account()
        self.register([self.ids[0], self.ids[3]], comboModalities=['Boxe', 'MMA'])
        self.assert_no_partial_account()

    def test_tampered_or_deleted_group_does_not_leave_account(self):
        for raw in ('[true]', '[1,1]', '{}', 'invalid', '[-1]', json.dumps([self.ids[0], 99999]), json.dumps([self.ids[2]])):
            with self.subTest(raw=raw):
                payload = self.registration_payload(regClassSelection=raw)
                self.client.post('/login', data={**payload, 'csrf_token': self.csrf()})
                self.assert_no_partial_account()

    def test_inactivated_unpublished_or_wrong_day_group_revalidated_on_submit(self):
        self.fixed_plan()
        for changes in ({'status': 'inativa'}, {'publish_public': False}, {'schedules': ['Ter • 19:00']}):
            with app.app_context():
                group = db.session.get(ClassGroup, self.ids[0])
                group.status, group.publish_public = 'ativa', True
                group.schedules = ['Seg • 19:00']
                for key, value in changes.items():
                    setattr(group, key, value)
                db.session.commit()
            self.register([self.ids[0]])
            self.assert_no_partial_account()

    def test_disabled_location_revalidated_on_submit(self):
        with app.app_context():
            Location.query.one().active = False
            db.session.commit()
        self.register([self.ids[0]])
        self.assert_no_partial_account()

    def test_minor_requires_guardian_and_configured_age_range(self):
        year = datetime.now().year - 10
        with app.app_context():
            group = db.session.get(ClassGroup, self.ids[0])
            group.min_age, group.max_age, group.audience = 7, 12, 'Kids'
            db.session.commit()
        self.register([self.ids[0]])
        self.assert_no_partial_account()
        self.register([self.ids[0]], regBirthDate=f'{year}-01-01')
        self.assert_no_partial_account()
        self.register([self.ids[0]], regBirthDate=f'{year}-01-01', imageGuardianName='Maria Responsável',
                      imageGuardianCpf='11144477735', imageGuardianRelationship='mae')
        with app.app_context():
            user = User.query.filter_by(username='novoaluno').one()
            self.assertEqual(user.image_consent_guardian_cpf, '11144477735')
            self.assertEqual(ClassPreference.query.count(), 1)
            self.assertEqual(ContractAcceptance.query.count(), 0)

    def test_database_failure_after_links_rolls_back_account(self):
        from app import save_registration_class_choices
        def fail_after_link(*args):
            save_registration_class_choices(*args)
            db.session.flush()
            raise SQLAlchemyError('Injected transaction failure')
        with patch('app.save_registration_class_choices', side_effect=fail_after_link):
            self.register([self.ids[0]])
        self.assert_no_partial_account()

    def test_resubmitting_same_cpf_does_not_duplicate_preferences(self):
        self.register([self.ids[0]])
        self.client.get('/login?logout=1')
        self.register([self.ids[0]], regCpf='52998224725', regUsername='outro', regEmail='outro@example.com')
        with app.app_context():
            self.assertEqual(ClassPreference.query.count(), 1)
            self.assertIsNone(User.query.filter_by(username='outro').first())

    def test_preferences_appear_in_portal_and_calendar_without_limiting_credits(self):
        self.register([self.ids[0]])
        dashboard = self.client.get('/dashboard').get_data(as_text=True)
        calendar = self.client.get('/calendario.html').get_data(as_text=True)
        self.assertIn('Turma 0', dashboard)
        self.assertIn('Seu horário de preferência', calendar)
        with app.app_context():
            user = User.query.filter_by(username='novoaluno').one()
            feed = personal_calendar_ics(user)
            self.assertIn('STATUS:TENTATIVE', feed)
            self.assertNotIn('SUMMARY:Turma 1', feed)
        for time in ('06:30', '19:00'):
            self.client.post('/presencas', data={'csrf_token': self.csrf(), 'class_slot': f'{self.ids[1]}|{time}'})
        with app.app_context():
            self.assertEqual(Attendance.query.count(), 2)
            self.assertEqual(ClassEnrollment.query.count(), 0)
        self.client.post('/presencas', data={'csrf_token': self.csrf(), 'class_slot': f'{self.ids[2]}|06:30'})
        with app.app_context():
            self.assertEqual(Attendance.query.count(), 2)

    def test_fixed_calendar_uses_contracted_days_and_live_schedule(self):
        self.fixed_plan()
        self.register([self.ids[0]], regTrainingDays='ter-qui')
        with app.app_context():
            user = User.query.filter_by(username='novoaluno').one()
            feed = personal_calendar_ics(user)
            self.assertIn('BYDAY=TU,TH;', feed)
            self.assertIn('STATUS:CONFIRMED', feed)
            group = db.session.get(ClassGroup, self.ids[0])
            group.schedules = ['Qui • 18:30']
            db.session.commit()
            self.assertIn('T183000', personal_calendar_ics(user))
            group.status = 'inativa'
            db.session.commit()
            self.assertNotIn('BEGIN:VEVENT', personal_calendar_ics(user))

    def test_register_and_checkin_locks_do_not_edit_class_timestamps(self):
        self.fixed_plan()
        with app.app_context():
            before = {group.id: group.updated_at for group in ClassGroup.query.all()}
        self.register([self.ids[0]], regTrainingDays='todos')
        self.client.post('/presencas', data={'csrf_token':self.csrf(), 'class_slot':f'{self.ids[0]}|06:30'})
        with app.app_context():
            self.assertEqual(Attendance.query.count(), 1)
            self.assertEqual(before, {group.id: group.updated_at for group in ClassGroup.query.all()})

    @unittest.skipUnless(base.test_database_url.startswith('postgresql'), 'Disputa de vaga exige PostgreSQL isolado')
    def test_concurrent_last_seat_creates_only_one_complete_account(self):
        from concurrent.futures import ThreadPoolExecutor
        from threading import Barrier
        from app import save_registration_class_choices
        self.fixed_plan()
        with app.app_context():
            db.session.get(ClassGroup, self.ids[0]).capacity = 1
            db.session.commit()
        barrier = Barrier(2)
        payloads = [self.registration_payload(regUsername=f'concorrente{i}', regEmail=f'concorrente{i}@example.invalid',
                    regCpf=cpf, regClassSelection=json.dumps([self.ids[0]]))
                    for i, cpf in enumerate(('52998224725', '11144477735'))]
        def synchronize(*args):
            barrier.wait(timeout=15)
            return save_registration_class_choices(*args)
        def send(payload):
            client = app.test_client()
            client.get('/login')
            with client.session_transaction() as session:
                token = session['_csrf_token']
            return client.post('/login', data={**payload, 'csrf_token': token}).headers['Location']
        with patch('app.save_registration_class_choices', side_effect=synchronize):
            with ThreadPoolExecutor(max_workers=2) as pool:
                destinations = list(pool.map(send, payloads))
        self.assertEqual(sum(destination.endswith('/dashboard') for destination in destinations), 1)
        with app.app_context():
            self.assertEqual(User.query.filter(User.username.like('concorrente%')).count(), 1)
            self.assertEqual(ClassEnrollment.query.count(), 1)
            self.assertEqual(ClassPreference.query.count(), 0)


if __name__ == '__main__':
    unittest.main()
