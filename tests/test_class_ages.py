"""Faixas são dados da academia; exemplos abaixo pertencem somente aos testes."""
import json
import re
import unittest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
import test_app as base
from app import app, db, ClassGroup, ClassEnrollment, User


class ClassAgeTests(unittest.TestCase):
    csrf = base.BJSportsTestCase.csrf
    login = base.BJSportsTestCase.login

    def setUp(self):
        base.BJSportsTestCase.setUp(self)
        with app.app_context():
            group = ClassGroup(name='Turma de ensaio etário', modality='Jiu-Jitsu',
                               audience='Kids', instructor='Instrutor', capacity=20,
                               status='ativa', publish_public=False)
            group.schedules = ['Seg • 19:00']
            db.session.add(group)
            db.session.flush()
            self.group_id = group.id
            db.session.add(ClassEnrollment(user_id=User.query.filter_by(username='aluno').one().id,
                                           class_group_id=group.id, active=True))
            db.session.commit()
        self.login('instrutor')

    def payload(self, **overrides):
        return dict(action='update', class_id=self.group_id, class_name='Turma de ensaio etário',
                    class_modality='Jiu-Jitsu', class_audience='Kids', class_schedule='Seg • 19:00',
                    class_instructor='Instrutor', class_capacity='20', class_duration='60',
                    class_status='ativa', class_location_slug='cajazeiras-sede',
                    csrf_token=self.csrf(), **overrides)

    def test_age_limits_start_undefined_even_for_kids(self):
        with app.app_context():
            group = db.session.get(ClassGroup, self.group_id)
            self.assertIsNone(group.min_age)
            self.assertIsNone(group.max_age)
            self.assertEqual(group.formatted_age_range, 'Faixa etária não definida')
        page = self.client.get('/gestao_turmas.html').get_data(as_text=True)
        self.assertIn('name="class_min_age"', page)
        self.assertIn('Faixa etária não definida', page)

    def test_instructor_saves_limits_without_changing_enrollment(self):
        page = self.client.post('/gestao_turmas.html', data=self.payload(
            class_min_age='7', class_max_age='12'), follow_redirects=True).get_data(as_text=True)
        self.assertIn('7 a 12 anos', page)
        self.assertIn('data-class-min-age="7"', page)
        detail = self.client.get(f'/gestao/turmas/{self.group_id}').get_data(as_text=True)
        self.assertIn('7 a 12 anos', detail)
        with app.app_context():
            group = db.session.get(ClassGroup, self.group_id)
            self.assertEqual((group.min_age, group.max_age, group.audience), (7, 12, 'Kids'))
            self.assertEqual(group.enrolled, 1)
            self.assertEqual(ClassEnrollment.query.count(), 1)

    def test_invalid_limits_preserve_record_and_form(self):
        with app.app_context():
            group = db.session.get(ClassGroup, self.group_id)
            group.min_age, group.max_age = 7, 12
            db.session.commit()
        for minimum, maximum in [('14', '8'), ('-1', '12'), ('7.5', '12'), ('7', '151'), ('idade', '12')]:
            with self.subTest(minimum=minimum, maximum=maximum):
                page = self.client.post('/gestao_turmas.html', data=self.payload(
                    class_min_age=minimum, class_max_age=maximum), follow_redirects=True).get_data(as_text=True)
                state = json.loads(re.search(r'id="classFormRestore">(.*?)</script>', page, re.S).group(1))
                self.assertEqual(state['data']['class_min_age'], minimum)
                self.assertEqual(state['data']['class_max_age'], maximum)
                with app.app_context():
                    group = db.session.get(ClassGroup, self.group_id)
                    self.assertEqual((group.min_age, group.max_age, group.enrolled), (7, 12, 1))

    def test_older_form_keeps_limits_and_explicit_blank_clears_them(self):
        self.client.post('/gestao_turmas.html', data=self.payload(class_min_age='0', class_max_age='1'))
        self.client.post('/gestao_turmas.html', data=self.payload())
        with app.app_context():
            group = db.session.get(ClassGroup, self.group_id)
            self.assertEqual((group.min_age, group.max_age), (0, 1))
        self.client.post('/gestao_turmas.html', data=self.payload(class_min_age='', class_max_age=''))
        with app.app_context():
            group = db.session.get(ClassGroup, self.group_id)
            self.assertEqual((group.min_age, group.max_age), (None, None))

    def test_one_sided_limits_and_zero_are_supported(self):
        for minimum, maximum, label in [('0', '', 'A partir de 0 anos'), ('', '1', 'Até 1 ano'), ('1', '1', '1 ano')]:
            self.client.post('/gestao_turmas.html', data=self.payload(class_min_age=minimum, class_max_age=maximum))
            with app.app_context():
                self.assertEqual(db.session.get(ClassGroup, self.group_id).formatted_age_range, label)

    def test_legacy_schedule_split_preserves_age_limits(self):
        from app import split_combined_muay_thai_class
        with app.app_context():
            group = db.session.get(ClassGroup, self.group_id)
            group.name, group.modality = 'Muay Thai', 'Muay Thai'
            group.schedules = ['Seg, Qua, Sex • 07:30 e 18:00']
            group.min_age, group.max_age = 7, 12
            db.session.commit()
            split_combined_muay_thai_class()
            evening = ClassGroup.query.filter_by(name='Muay Thai Noite').one()
            self.assertEqual((evening.min_age, evening.max_age), (7, 12))
            self.assertEqual((group.min_age, group.max_age), (7, 12))

    def test_database_rejects_invalid_limits_and_monitor_cannot_edit(self):
        with app.app_context():
            for minimum, maximum in [(10, 4), (-1, 9), (0, 151)]:
                with self.assertRaises(IntegrityError):
                    db.session.execute(text('UPDATE class_group SET min_age=:minimum, max_age=:maximum WHERE id=:id'),
                                       dict(minimum=minimum, maximum=maximum, id=self.group_id))
                    db.session.commit()
                db.session.rollback()
        self.login('monitor')
        self.assertEqual(self.client.post('/gestao_turmas.html', data=self.payload(
            class_min_age='7', class_max_age='12')).status_code, 302)
        with app.app_context():
            self.assertIsNone(db.session.get(ClassGroup, self.group_id).min_age)
