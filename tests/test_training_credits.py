import unittest
from datetime import date, datetime, timedelta
from unittest.mock import patch
import test_app as base
from app import (app, db, User, Plan, Attendance, ClassGroup, training_credit_balance,
                 credit_contract, migrate_attendance_occurrences, apply_individual_credit_prices, migrate_legacy_boxe_frequency)
from training_credits import billing_period, weekly_allowance
from sqlalchemy import text


class TrainingCreditsTests(unittest.TestCase):
    setUp = base.BJSportsTestCase.setUp
    csrf = base.BJSportsTestCase.csrf
    login = base.BJSportsTestCase.login

    def prepare(self, frequency=2, modality='Boxe'):
        today = datetime.now().date()
        with app.app_context():
            user = User.query.filter_by(username='aluno').one()
            user.plan = f'Plano {modality} • {frequency} aulas por semana — R$ 90,00/mês'
            user.due_date = str(today.day)
            user.created_at = datetime(today.year, today.month, today.day) - timedelta(days=60)
            db.session.add(Plan(name=f'Plano {modality}', category='Planos Individuais',
                                modality=modality, price='R$ 90,00/mês'))
            group = ClassGroup(name='Boxe flexível', modality=modality, audience='Adulto',
                               instructor='Instrutor', status='ativa', capacity=20)
            weekday = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'][today.weekday()]
            group.schedules = [f'{weekday} • 06:00 e 18:00 e 20:00']
            db.session.add(group)
            db.session.commit()
            self.user_id, self.group_id = user.id, group.id
        self.login('aluno')

    def checkin(self, time, group_id=None):
        with patch.object(User, 'has_overdue_payments', return_value=False):
            return self.client.post('/presencas', data={'class_slot': f'{group_id or self.group_id}|{time}',
                'csrf_token': self.csrf()}, follow_redirects=True)

    def test_two_classes_same_day_and_no_third_credit(self):
        self.prepare()
        self.checkin('06:00')
        self.checkin('18:00')
        response = self.checkin('20:00')
        self.assertIn('Sem créditos disponíveis', response.get_data(as_text=True))
        with app.app_context():
            self.assertEqual(Attendance.query.count(), 2)
            self.assertEqual(training_credit_balance(db.session.get(User, self.user_id))['remaining'], 0)

    def test_duplicate_class_does_not_consume_twice(self):
        self.prepare()
        self.checkin('06:00')
        self.checkin('06:00')
        with app.app_context():
            self.assertEqual(Attendance.query.count(), 1)

    def test_rejected_request_releases_credit(self):
        self.prepare()
        self.checkin('06:00')
        self.checkin('18:00')
        with app.app_context():
            record = Attendance.query.first()
            record_id = record.id
        self.login('instrutor')
        self.client.post('/presencas', data={'action': 'reject_attendance', 'attendance_id': record_id,
                                             'csrf_token': self.csrf()})
        self.login('aluno')
        self.checkin('20:00')
        with app.app_context():
            self.assertEqual(Attendance.query.filter_by(status='pendente').count(), 2)
            self.assertEqual(Attendance.query.filter_by(status='negado').count(), 1)

    def test_other_modality_and_invalid_time_rejected(self):
        self.prepare()
        with app.app_context():
            group = ClassGroup(name='Outra modalidade', modality='Muay Thai', audience='Adulto',
                               instructor='Instrutor', status='ativa')
            group.schedules = db.session.get(ClassGroup, self.group_id).schedules
            db.session.add(group)
            db.session.commit()
            other_id = group.id
        self.assertIn('modalidade contratada', self.checkin('06:00', other_id).get_data(as_text=True))
        self.checkin('09:59')
        with app.app_context():
            self.assertEqual(Attendance.query.count(), 0)

    def test_accumulation_and_expiration_for_both_limited_plans(self):
        self.prepare()
        with app.app_context():
            user = db.session.get(User, self.user_id)
            user.created_at = datetime(2025, 1, 1)
            user.due_date = '10'
            for quota in (2, 3):
                user.plan = f'Plano Boxe • {quota} aulas por semana — R$ 90,00/mês'
                self.assertEqual(training_credit_balance(user, date(2026, 9, 10))['remaining'], quota)
                self.assertEqual(training_credit_balance(user, date(2026, 9, 17))['remaining'], quota * 2)
                self.assertEqual(training_credit_balance(user, date(2026, 10, 10))['remaining'], quota)
                self.assertEqual(training_credit_balance(user, date(2026, 9, 17))['expires'], date(2026, 10, 10))

    def test_unlimited_and_mma_exclusion(self):
        self.prepare()
        with app.app_context():
            user = db.session.get(User, self.user_id)
            user.plan = 'Plano Boxe • Ilimitado — R$ 120,00/mês'
            db.session.commit()
            self.assertIsNone(training_credit_balance(user)['remaining'])
        for time in ('06:00', '18:00', '20:00'):
            self.checkin(time)
        with app.app_context():
            self.assertEqual(Attendance.query.count(), 3)
            user = db.session.get(User, self.user_id)
            db.session.add(Plan(name='MMA', modality='MMA', category='Planos Individuais', price='R$ 130,00/mês'))
            user.plan = 'MMA • 2 aulas por semana — R$ 130,00/mês'
            self.assertIsNone(credit_contract(user))

    def test_catalog_migration_preserves_mma_and_is_idempotent(self):
        with app.app_context():
            db.session.execute(text('DELETE FROM business_rule_migration'))
            for modality in ('Jiu-Jitsu', 'Boxe', 'Muay Thai', 'MMA'):
                db.session.add(Plan(name=modality, modality=modality, category='Planos Individuais', price='R$ 130,00/mês'))
            db.session.commit()
            apply_individual_credit_prices()
            for plan in Plan.query.filter(Plan.modality.isnot(None)).all():
                if plan.modality == 'MMA':
                    self.assertEqual(plan.price, 'R$ 130,00/mês')
                else:
                    self.assertEqual(plan.price_ter_qui, 'R$ 90,00/mês')
                    self.assertEqual(plan.price_seg_qua_sex, 'R$ 100,00/mês')
                    self.assertEqual(plan.price_all_days, 'R$ 120,00/mês')
            plan = Plan.query.filter_by(modality='Boxe').one()
            plan.price_ter_qui = 'R$ 95,00/mês'
            db.session.commit()
            apply_individual_credit_prices()
            db.session.expire_all()
            self.assertEqual(plan.price_ter_qui, 'R$ 95,00/mês')

    def test_legacy_migration_keeps_history_and_allows_two_occurrences(self):
        self.prepare()
        with app.app_context():
            db.session.remove()
            with db.engine.begin() as conn:
                conn.execute(text('DROP TABLE attendance'))
                conn.execute(text('CREATE TABLE attendance (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, class_group_id INTEGER, training_date DATE NOT NULL, modality VARCHAR(60), status VARCHAR(20), confirmed_by_username VARCHAR(80), confirmed_at DATETIME, created_at DATETIME, CONSTRAINT uq_attendance_day UNIQUE(user_id, training_date))'))
                conn.execute(text("INSERT INTO attendance VALUES (42, :uid, :gid, '2026-08-01', 'Boxe', 'confirmado', 'instrutor', NULL, NULL)"), {'uid': self.user_id, 'gid': self.group_id})
            migrate_attendance_occurrences()
            migrate_attendance_occurrences()
            record = db.session.get(Attendance, 42)
            self.assertEqual(record.status, 'confirmado')
            self.assertEqual(record.modality, 'Boxe')
        self.checkin('06:00')
        self.checkin('18:00')
        with app.app_context():
            self.assertEqual(Attendance.query.count(), 3)

    def test_full_class_and_overdue_do_not_consume_credit(self):
        self.prepare()
        with app.app_context():
            group = db.session.get(ClassGroup, self.group_id)
            group.capacity = 0
            db.session.commit()
        self.assertIn('lotada', self.checkin('06:00').get_data(as_text=True))
        with patch.object(User, 'has_overdue_payments', return_value=True):
            self.client.post('/presencas', data={'class_slot': f'{self.group_id}|18:00',
                                                'csrf_token': self.csrf()})
        with app.app_context():
            self.assertEqual(Attendance.query.count(), 0)

    def test_confirmation_keeps_one_credit_reserved(self):
        self.prepare()
        self.checkin('06:00')
        with app.app_context():
            record_id = Attendance.query.one().id
        self.login('instrutor')
        self.client.post('/presencas', data={'action': 'confirm_attendance', 'attendance_id': record_id,
                                             'csrf_token': self.csrf()})
        with app.app_context():
            self.assertEqual(training_credit_balance(db.session.get(User, self.user_id))['remaining'], 1)
            self.assertEqual(Attendance.query.one().status, 'confirmado')

    def test_due_date_change_does_not_reset_active_credit_period(self):
        self.prepare()
        self.checkin('06:00')
        with app.app_context():
            user = db.session.get(User, self.user_id)
            before = training_credit_balance(user)
            user.due_date = '15' if user.due_date != '15' else '5'
            db.session.commit()
            after = training_credit_balance(user)
            self.assertEqual(before['start'], after['start'])
            self.assertEqual(before['expires'], after['expires'])
            self.assertEqual(after['remaining'], 1)

    def test_approved_legacy_boxe_frequency_migration(self):
        self.prepare()
        with app.app_context():
            db.session.execute(text("DELETE FROM business_rule_migration WHERE version = 'legacy-boxe-three-weekly-2026-09-11'"))
            user = db.session.get(User, self.user_id)
            user.plan = 'Boxe — R$ 90,00/mês'
            db.session.commit()
            migrate_legacy_boxe_frequency()
            db.session.expire_all()
            self.assertEqual(credit_contract(user), {'modality': 'Boxe', 'weekly': 3})
            self.assertEqual(user.get_plan_price(), 100)
            user.plan = 'Plano Boxe • Ilimitado — R$ 120,00/mês'
            db.session.commit()
            migrate_legacy_boxe_frequency()
            db.session.expire_all()
            self.assertIn('Ilimitado', user.plan)

    def test_calendar_boundaries_and_legacy_frequency(self):
        self.assertEqual(billing_period(date(2026, 1, 2), 10), (date(2025, 12, 10), date(2026, 1, 10)))
        self.assertEqual(billing_period(date(2026, 2, 28), 31), (date(2026, 2, 28), date(2026, 3, 31)))
        self.assertEqual(weekly_allowance('Jiu-Jitsu (Seg, Qua, Sex) • 2 aulas por semana — R$ 90'), 2)
        self.assertEqual(weekly_allowance('Jiu-Jitsu (Seg, Qua, Sex) — R$ 100'), 3)
