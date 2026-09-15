"""Consulta pública da grade no cadastro, sem matrícula ou reserva."""
import unittest
import test_app as base
from app import app, db, ClassGroup, ClassEnrollment, Location, User, Booking


class RegistrationScheduleTests(unittest.TestCase):
    csrf = base.BJSportsTestCase.csrf
    login = base.BJSportsTestCase.login

    def setUp(self):
        base.BJSportsTestCase.setUp(self)
        with app.app_context():
            db.session.add(Location(slug='unidade-teste', name='Unidade Teste', city='Cidade Teste', address='Endereço de teste', active=True))
            group = ClassGroup(name='Boxe de teste', modality='Boxe', audience='Adulto',
                               instructor='Professor Teste', location_slug='unidade-teste', capacity=2)
            group.schedules = ['Seg, Qua • 06:30 e 19:00']
            db.session.add(group)
            db.session.commit()
            self.group_id = group.id

    def catalog(self):
        response = self.client.get('/api/cadastro/turmas')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Cache-Control'], 'no-store')
        return response.get_json()['classes']

    def test_only_public_active_groups_with_active_explicit_location(self):
        with app.app_context():
            db.session.add(Location(slug='inativa', name='Unidade Inativa', city='Teste', address='Endereço de teste', active=False))
            for name, status, published, location in [
                ('Privada', 'ativa', False, 'unidade-teste'),
                ('Inativa', 'inativa', True, 'unidade-teste'),
                ('Unidade inativa', 'ativa', True, 'inativa'),
                ('Sem unidade', 'ativa', True, 'inexistente'),
                ('Lotada', 'lotada', True, 'unidade-teste'),
            ]:
                db.session.add(ClassGroup(name=name, modality='Boxe', status=status,
                                          publish_public=published, location_slug=location))
            db.session.commit()
        rows = self.catalog()
        self.assertEqual({row['name'] for row in rows}, {'Boxe de teste', 'Lotada'})
        self.assertTrue(next(row for row in rows if row['name'] == 'Lotada')['full'])

    def test_capacity_uses_only_active_enrollments_without_promising_a_seat(self):
        with app.app_context():
            group = db.session.get(ClassGroup, self.group_id)
            group.capacity = 1
            user = User.query.filter_by(username='aluno').one()
            enrollment = ClassEnrollment(user_id=user.id, class_group_id=group.id, active=False)
            db.session.add(enrollment)
            db.session.commit()
        self.assertFalse(self.catalog()[0]['full'])
        with app.app_context():
            ClassEnrollment.query.one().active = True
            db.session.commit()
        self.assertTrue(self.catalog()[0]['full'])

    def test_catalog_exposes_only_public_fields_and_preserves_unknown_age(self):
        row = self.catalog()[0]
        self.assertEqual(set(row), {'id', 'name', 'modality', 'audience', 'age_label',
                                   'min_age', 'max_age', 'instructor', 'schedules', 'location', 'full'})
        self.assertEqual(set(row['location']), {'slug', 'name', 'city'})
        self.assertEqual(row['age_label'], 'Faixa etária não definida')
        self.assertEqual(row['schedules'], [
            {'days': 'Seg, Qua', 'time': '06:30', 'period': 'manha'},
            {'days': 'Seg, Qua', 'time': '19:00', 'period': 'noite'},
        ])
        with app.app_context():
            group = db.session.get(ClassGroup, self.group_id)
            group.schedules = ['Inválido • 12:00', 'Seg • 25:00', None]
            db.session.commit()
        self.assertEqual(self.catalog()[0]['schedules'], [])

    def test_management_update_is_visible_in_next_catalog_request(self):
        self.login('instrutor')
        response = self.client.post('/gestao_turmas.html', data={
            'csrf_token': self.csrf(), 'action': 'update', 'class_id': self.group_id,
            'class_name': 'Boxe atualizado', 'class_modality': 'Boxe', 'class_audience': 'Kids',
            'class_min_age': '7', 'class_max_age': '12', 'class_schedule': 'Sáb • 15:30',
            'class_instructor': 'Professor Atualizado', 'class_capacity': '12',
            'class_duration': '60', 'class_status': 'ativa', 'class_location_slug': 'unidade-teste',
            'publish_public': '1',
        })
        self.assertEqual(response.status_code, 302)
        row = self.catalog()[0]
        self.assertEqual(row['name'], 'Boxe atualizado')
        self.assertEqual(row['age_label'], '7 a 12 anos')
        self.assertEqual(row['schedules'], [{'days': 'Sáb', 'time': '15:30', 'period': 'tarde'}])
        self.assertEqual(row['instructor'], 'Professor Atualizado')

    def test_consultation_does_not_create_accounts_enrollments_or_bookings(self):
        with app.app_context():
            before = (User.query.count(), ClassEnrollment.query.count(), Booking.query.count())
        self.catalog()
        page = self.client.get('/login?mode=register').get_data(as_text=True)
        self.assertIn('regClassSelection', page)
        with app.app_context():
            self.assertEqual(before, (User.query.count(), ClassEnrollment.query.count(), Booking.query.count()))
