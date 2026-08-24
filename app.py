import os
import json
import re
import urllib.parse
import secrets
import click
import tempfile
from decimal import Decimal, ROUND_HALF_UP
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file, Response, g
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text, or_, func
from itsdangerous import URLSafeSerializer, BadSignature
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, datetime, timedelta
from store_catalog import STORE_PRODUCTS
from financial_reports import build_financial_markdown, markdown_to_pdf, financial_report_to_xlsx

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'bjsports-production-secret-key-2026-cajazeiras')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///bjsports.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False
class CustomSessionInterface(Flask.session_interface.__class__):
    def get_cookie_secure(self, app):
        return False
    def save_session(self, app, session, response):
        app.config['SESSION_COOKIE_SECURE'] = False
        super().save_session(app, session, response)
        if 'Set-Cookie' in response.headers:
            cookies = response.headers.getlist('Set-Cookie')
            new_cookies = ['; '.join([p.strip() for p in c.split(';') if p.strip().lower() != 'secure']) for c in cookies]
            response.headers.setlist('Set-Cookie', new_cookies)

app.session_interface = CustomSessionInterface()

class HTTPFixMiddleware:
    def __init__(self, app_wsgi):
        self.app_wsgi = app_wsgi

    def __call__(self, environ, start_response):
        if '147.79.110.132' in environ.get('HTTP_HOST', '') or '5050' in environ.get('HTTP_HOST', '') or environ.get('SERVER_PORT') == '5050':
            environ['wsgi.url_scheme'] = 'http'
            environ.pop('HTTP_X_FORWARDED_PROTO', None)
        return self.app_wsgi(environ, start_response)

app.wsgi_app = HTTPFixMiddleware(app.wsgi_app)





if os.getenv('FLASK_ENV') == 'production' and not os.getenv('SECRET_KEY'):
    raise RuntimeError('SECRET_KEY é obrigatória em produção.')

db = SQLAlchemy(app)
calendar_token_serializer = URLSafeSerializer(app.config['SECRET_KEY'], salt='personal-calendar-feed')

ROLE_LEVEL = {'aluno': 0, 'monitor': 1, 'instrutor': 2, 'professor': 2}
MEMBERSHIP_TERMS_VERSION = '2026-08-17.4'
PRIVACY_NOTICE_VERSION = '2026-08-17'
BELT_COLORS = {'branca', 'azul', 'roxa', 'marrom', 'preta'}
BELT_LABELS = {'branca': 'Branca', 'azul': 'Azul', 'roxa': 'Roxa', 'marrom': 'Marrom', 'preta': 'Preta'}
DEFAULT_CLASS_GROUPS = [
    {'id': 1, 'name': 'Jiu-Jitsu Kids 1', 'modality': 'Jiu-Jitsu', 'audience': 'Kids',
     'schedules': ['Ter, Qui • 17:00'], 'weekly_sessions': 2, 'instructor': 'Mestre Bolivar',
     'capacity': 16, 'waiting': 0, 'status': 'ativa'},
    {'id': 2, 'name': 'Jiu-Jitsu Kids 2', 'modality': 'Jiu-Jitsu', 'audience': 'Kids',
     'schedules': ['Seg, Qua • 16:00'], 'weekly_sessions': 2, 'instructor': 'Mestre Bolivar',
     'capacity': 16, 'waiting': 0, 'status': 'ativa'},
    {'id': 3, 'name': 'Jiu-Jitsu / Meio dia', 'modality': 'Jiu-Jitsu', 'audience': 'Adulto',
     'schedules': ['Ter, Qui • 12:00'], 'weekly_sessions': 2, 'instructor': 'Mestre Bolivar',
     'capacity': 20, 'waiting': 0, 'status': 'ativa'},
    {'id': 4, 'name': 'Jiu-Jitsu Tarde', 'modality': 'Jiu-Jitsu', 'audience': 'Adulto',
     'schedules': ['Seg, Qua, Sex • 17:00'], 'weekly_sessions': 3, 'instructor': 'Mestre Bolivar',
     'capacity': 20, 'waiting': 0, 'status': 'ativa'},
    {'id': 5, 'name': 'Jiu-Jitsu Noturno', 'modality': 'Jiu-Jitsu', 'audience': 'Adulto',
     'schedules': ['Seg, Qua, Sex • 19:00', 'Ter, Qui • 19:00'], 'weekly_sessions': 5,
     'instructor': 'Mestre Bolivar', 'capacity': 20, 'waiting': 0, 'status': 'ativa'},
    {'id': 6, 'name': 'Boxe Matinal', 'modality': 'Boxe', 'audience': 'Adulto',
     'schedules': ['Seg, Qua, Sex • 06:00'], 'weekly_sessions': 3, 'instructor': 'Mestre Bolivar',
     'capacity': 20, 'waiting': 0, 'status': 'ativa'},
    {'id': 7, 'name': 'Boxe Noturno', 'modality': 'Boxe', 'audience': 'Adulto',
     'schedules': ['Ter, Qui • 19:00'], 'weekly_sessions': 2, 'instructor': 'Mestre Bolivar',
     'capacity': 20, 'waiting': 0, 'status': 'ativa'},
    {'id': 8, 'name': 'Muay Thai Kids', 'modality': 'Muay Thai', 'audience': 'Kids',
     'schedules': ['Ter, Qui • 18:00'], 'weekly_sessions': 2, 'instructor': 'Mestre Bolivar',
     'capacity': 16, 'waiting': 0, 'status': 'ativa'},
    {'id': 9, 'name': 'Muay Thai', 'modality': 'Muay Thai', 'audience': 'Adulto',
     'schedules': ['Seg, Qua, Sex • 07:30 e 18:00', 'Ter, Qui • 20:00'], 'weekly_sessions': 8,
     'instructor': 'Mestre Bolivar', 'capacity': 20, 'waiting': 0, 'status': 'ativa'},
    {'id': 10, 'name': 'MMA Profissional', 'modality': 'MMA', 'audience': 'Profissional',
     'schedules': ['Seg, Qua, Sex • 11:30'], 'weekly_sessions': 3, 'instructor': 'Mestre Bolivar',
     'capacity': 20, 'waiting': 0, 'status': 'ativa'},
    {'id': 11, 'name': 'MMA Amador / Iniciantes', 'modality': 'MMA', 'audience': 'Iniciantes',
     'schedules': ['Ter, Qui • 18:00'], 'weekly_sessions': 2, 'instructor': 'Mestre Bolivar',
     'capacity': 20, 'waiting': 0, 'status': 'ativa'},
]
CHAMPIONSHIP_WEIGHT_COLUMNS = [
    ('pre_mirim', 'Pré-Mirim 1, 2 e 3', '4, 5 e 6 anos'),
    ('mirim', 'Mirim 1, 2 e 3', '7, 8 e 9 anos'),
    ('infantil', 'Infantil 1, 2 e 3', '10, 11 e 12 anos'),
    ('infanto', 'Infanto 1 e 2', '13, 14 e 15 anos'),
    ('juvenil', 'Juvenil 1 e 2', '16 e 17 anos'),
    ('adulto_master', 'Adulto e Master', ''),
]
CHAMPIONSHIP_WEIGHT_SEED = {
    'masculino': [
        ('Galo', '', '', 'Até 32,2 kg', 'Até 44,3 kg', 'Até 53,5 kg', 'Até 57,5 kg'),
        ('Pluma', 'Até 17,9 kg', 'Até 24 kg', 'Até 36,2 kg', 'Até 48,3 kg', 'Até 58,5 kg', 'Até 64 kg'),
        ('Pena', 'Até 20,0 kg', 'Até 27,0 kg', 'Até 40,3 kg', 'Até 52,5 kg', 'Até 64 kg', 'Até 70 kg'),
        ('Leve', 'Até 24,0 kg', 'Até 30,2 kg', 'Até 44,3 kg', 'Até 56,5 kg', 'Até 69 kg', 'Até 76 kg'),
        ('Médio', 'Até 26,0 kg', 'Até 33,2 kg', 'Até 48,3 kg', 'Até 60,5 kg', 'Até 74 kg', 'Até 82,3 kg'),
        ('Meio Pesado', 'Até 29,0 kg', 'Até 36,2 kg', 'Até 52,5 kg', 'Até 65 kg', 'Até 79,3 kg', 'Até 88,3 kg'),
        ('Pesado', 'Até 32,0 kg', 'Até 39,3 kg', 'Até 56,5 kg', 'Até 69 kg', 'Até 84,3 kg', 'Até 94,3 kg'),
        ('Super Pesado', 'Até 35,0 kg', 'Até 42,3 kg', 'Até 60,5 kg', 'Até 73 kg', 'Até 89,3 kg', 'Até 100,5 kg'),
        ('Pesadíssimo', 'Acima de 35,0 kg', '+ 42,3 kg', '+ 60,5 kg', '+ 73 kg', '+ 89,3 kg', '+ 100,5 kg'),
    ],
    'feminino': [
        ('Galo', '', '', 'Até 32,2 kg', 'Até 44,3 kg', 'Até 44,3 kg', 'Até 48,5 kg'),
        ('Pluma', 'Até 17,9 kg', 'Até 24 kg', 'Até 36,2 kg', 'Até 48,3 kg', 'Até 48,3 kg', 'Até 53,5 kg'),
        ('Pena', 'Até 20,0 kg', 'Até 27,0 kg', 'Até 40,3 kg', 'Até 52,5 kg', 'Até 52,5 kg', 'Até 58,5 kg'),
        ('Leve', 'Até 24,0 kg', 'Até 30,2 kg', 'Até 44,3 kg', 'Até 56,5 kg', 'Até 56,5 kg', 'Até 64 kg'),
        ('Médio', 'Até 26,0 kg', 'Até 33,2 kg', 'Até 48,3 kg', 'Até 60,5 kg', 'Até 60,5 kg', 'Até 69 kg'),
        ('Meio Pesado', 'Até 29,0 kg', 'Até 36,2 kg', 'Até 52,5 kg', 'Até 65 kg', 'Até 65 kg', 'Até 74 kg'),
        ('Pesado', 'Até 32,0 kg', 'Até 39,3 kg', 'Até 56,5 kg', 'Até 69 kg', 'Até 69 kg', 'Até 79,3 kg'),
        ('Super Pesado', 'Até 35,0 kg', 'Até 42,3 kg', 'Até 60,5 kg', 'Até 73 kg', 'Até 73 kg', 'Até 84,3 kg'),
        ('Pesadíssimo', 'Acima de 35,0 kg', '+ 42,3 kg', '+ 60,5 kg', '+ 73 kg', '', ''),
    ],
}

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            flash('Entre na sua conta para continuar.', 'warning')
            return redirect(url_for('login', next=request.path))
        return view(*args, **kwargs)
    return wrapped

def role_required(minimum_role):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if 'user_id' not in session:
                flash('Entre na sua conta para continuar.', 'warning')
                return redirect(url_for('login', next=request.path))
            if ROLE_LEVEL.get(session.get('user_role'), -1) < ROLE_LEVEL[minimum_role]:
                flash('Você não tem permissão para acessar esta área.', 'error')
                return redirect(url_for('login'))
            return view(*args, **kwargs)
        return wrapped
    return decorator

def csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = secrets.token_urlsafe(32)
    return session['_csrf_token']

def is_valid_cpf(value):
    digits = ''.join(c for c in value if c.isdigit())
    if len(digits) != 11 or digits == digits[0] * 11:
        return False
    for size in (9, 10):
        total = sum(int(digits[index]) * (size + 1 - index) for index in range(size))
        check = (total * 10 % 11) % 10
        if check != int(digits[size]):
            return False
    return True

def get_attendance_modality(plan_name):
    normalized = (plan_name or '').lower()
    if 'passe livre' in normalized:
        return 'Treino livre'
    if 'muay thai' in normalized:
        return 'Muay Thai'
    if 'boxe' in normalized and 'jiu' not in normalized and 'bjj' not in normalized:
        return 'Boxe'
    if 'jiu' in normalized or 'bjj' in normalized:
        return 'Jiu-Jitsu'
    return 'Treino'

def format_enrollment_duration(started_at, reference=None):
    if not started_at:
        return 'data não informada'
    reference = reference or datetime.now()
    start_date = started_at.date() if hasattr(started_at, 'date') else started_at
    reference_date = reference.date() if hasattr(reference, 'date') else reference
    total_months = max(0, (reference_date.year - start_date.year) * 12
                       + reference_date.month - start_date.month
                       - (1 if reference_date.day < start_date.day else 0))
    if total_months == 0:
        return 'menos de 1 mês'
    years, months = divmod(total_months, 12)
    parts = []
    if years:
        parts.append(f'{years} ano' if years == 1 else f'{years} anos')
    if months:
        parts.append(f'{months} mês' if months == 1 else f'{months} meses')
    return ' e '.join(parts)

@app.before_request
def protect_csrf():
    if request.method in {'POST', 'PUT', 'PATCH', 'DELETE'}:
        supplied = request.form.get('csrf_token') or request.headers.get('X-CSRF-Token')
        stored = session.get('_csrf_token', '')
        if not supplied:
            return jsonify({'error': 'Token CSRF ausente.'}), 400
        if stored and not secrets.compare_digest(supplied, stored):
            return jsonify({'error': 'Token CSRF inválido.'}), 400
        if not stored:
            session['_csrf_token'] = supplied

@app.before_request
def require_password_change():
    if not session.get('user_id') or request.endpoint in {
        'change_temporary_password', 'logout', 'static', 'login'
    }:
        return None
    user = db.session.get(User, session['user_id'])
    if user and user.must_change_password:
        return redirect(url_for('change_temporary_password'))

@app.after_request
def add_security_headers(response):
    response.headers.setdefault('X-Content-Type-Options', 'nosniff')
    response.headers.setdefault('X-Frame-Options', 'SAMEORIGIN')
    response.headers.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
    if 'Set-Cookie' in response.headers:
        cookies = response.headers.getlist('Set-Cookie')
        new_cookies = [c.replace('; Secure', '').replace('; secure', '') if 'session=' in c else c for c in cookies]
        response.headers.setlist('Set-Cookie', new_cookies)
    return response
    return response

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    ddd = db.Column(db.String(2), nullable=False)
    phone = db.Column(db.String(9), nullable=False)
    email = db.Column(db.String(254), unique=True)
    sex = db.Column(db.String(20), nullable=False, default='prefer_not')
    plan = db.Column(db.String(150), nullable=False)
    due_date = db.Column(db.String(10), default='5') # Dia 5, 15 ou 25
    initial_due_date = db.Column(db.String(10), nullable=True) # Dia de vencimento do cadastro original
    start_month = db.Column(db.Integer, default=5) # Mês de início (ex: 5 para Maio)
    role = db.Column(db.String(30), default='aluno') # 'aluno', 'monitor', 'instrutor'
    payment_status = db.Column(db.String(30), default='Em Dia') # 'Em Dia', 'Pendente'
    monthly_fee_exempt = db.Column(db.Boolean, nullable=False, default=False)
    fee_exempted_by_username = db.Column(db.String(80))
    fee_exempted_at = db.Column(db.DateTime)
    monthly_history = db.Column(db.Text, default='{}') # JSON string de status dos meses
    password_hash = db.Column(db.String(256), nullable=False)
    belt_color = db.Column(db.String(20), nullable=False, default='branca')
    belt_degree = db.Column(db.Integer, nullable=False, default=0)
    membership_terms_version = db.Column(db.String(20))
    membership_terms_accepted_at = db.Column(db.DateTime)
    privacy_notice_version = db.Column(db.String(20))
    privacy_notice_accepted_at = db.Column(db.DateTime)
    image_use_consent = db.Column(db.Boolean, nullable=False, default=False)
    image_use_consent_at = db.Column(db.DateTime)
    image_consent_scope = db.Column(db.String(20), nullable=False, default='none')
    image_consent_guardian_name = db.Column(db.String(120))
    image_consent_guardian_cpf = db.Column(db.String(14))
    image_consent_guardian_relationship = db.Column(db.String(30))
    medical_restriction = db.Column(db.String(250))
    is_experimental = db.Column(db.Boolean, nullable=False, default=False)
    selected_modalities = db.Column(db.String(250)) # ex: "Jiu-Jitsu, Boxe"
    sponsor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, index=True)
    sponsored_previous_plan = db.Column(db.String(150), nullable=True)
    sponsored_previous_modalities = db.Column(db.String(250), nullable=True)
    sponsor_started_at = db.Column(db.DateTime, nullable=True)
    sponsored_dependents = db.relationship(
        'User', backref=db.backref('plan_sponsor', remote_side=[id]),
        foreign_keys=[sponsor_id], lazy=True,
    )
    birth_date = db.Column(db.Date)
    must_change_password = db.Column(db.Boolean, nullable=False, default=False)
    password_reset_by_username = db.Column(db.String(80))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def original_due_day(self):
        if hasattr(self, 'initial_due_date') and self.initial_due_date and str(self.initial_due_date).isdigit():
            return int(self.initial_due_date)
        ca = getattr(self, 'created_at', None)
        if ca and hasattr(ca, 'day'):
            d = ca.day
            return d if d <= 28 else 28
        if hasattr(self, 'due_date') and self.due_date and str(self.due_date).isdigit():
            return int(self.due_date)
        return 5

    def get_selected_modalities_list(self):
        if not self.selected_modalities:
            return []
        return [m.strip() for m in self.selected_modalities.split(',') if m.strip()]

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_overdue_payments(self):
        return self.get_overdue_details()['count'] > 0

    def get_trial_status(self):
        """Calcula o status do período de experiência gratuita de 60h para o aluno."""
        if self.role != 'aluno' or self.payment_status == 'Em Dia':
            return {'in_trial': False, 'expired': False, 'hours_left': 0}
        
        ref_time = self.created_at or self.membership_terms_accepted_at or datetime.utcnow()
        elapsed_seconds = (datetime.utcnow() - ref_time).total_seconds()
        elapsed_hours = elapsed_seconds / 3600.0
        
        if elapsed_hours <= 60.0:
            hours_left = max(1, int(round(60.0 - elapsed_hours)))
            return {'in_trial': True, 'expired': False, 'hours_left': hours_left}
        else:
            return {'in_trial': False, 'expired': True, 'hours_left': 0}

    def can_be_managed_by(self, actor_user):
        """
        Verifica se um instrutor ou monitor tem permissão para dar baixa na mensalidade deste aluno.
        Instrutor: Pode dar baixa em qualquer aluno.
        Monitor: Pode dar baixa apenas se o aluno pertencer a uma turma onde o monitor é o instrutor/monitor responsável ou se compartilharem turma.
        """
        if not actor_user:
            return False
        if actor_user.role in {'instrutor', 'professor'}:
            return True
        if actor_user.role == 'monitor':
            monitor_groups = ClassGroup.query.filter(
                (ClassGroup.responsible_monitor_id == actor_user.id) |
                (ClassGroup.instructor.ilike(f'%{actor_user.name}%')) |
                (ClassGroup.instructor.ilike(f'%{actor_user.username}%'))
            ).all()
            monitor_group_ids = {g.id for g in monitor_groups}

            monitor_enrollments = ClassEnrollment.query.filter_by(user_id=actor_user.id, active=True).all()
            monitor_group_ids.update({e.class_group_id for e in monitor_enrollments})

            student_enrollments = ClassEnrollment.query.filter_by(user_id=self.id, active=True).all()
            student_group_ids = {e.class_group_id for e in student_enrollments}

            if monitor_group_ids.intersection(student_group_ids):
                return True

            student_attendances = Attendance.query.filter_by(user_id=self.id).all()
            student_att_groups = {a.class_group_id for a in student_attendances if a.class_group_id}
            if monitor_group_ids.intersection(student_att_groups):
                return True

            if not student_group_ids and monitor_groups:
                monitor_modalities = {g.modality.lower() for g in monitor_groups}
                student_plan = (self.plan or '').lower()
                if any(m in student_plan for m in monitor_modalities if m):
                    return True

            return False
        return False

    def is_fee_exempt_for(self, year=None, month=None):
        today = datetime.now()
        year, month = year or today.year, month or today.month
        period_key = year * 100 + month
        if self.sponsor_id and self.sponsor_started_at:
            sponsor_period = self.sponsor_started_at.year * 100 + self.sponsor_started_at.month
            if period_key >= sponsor_period:
                return True
        if self.fee_exemptions:
            return any(exemption.covers(year, month) for exemption in self.fee_exemptions)
        return bool(self.monthly_fee_exempt and period_key >= (today.year * 100 + today.month))

    def get_month_history_dict(self):
        try:
            return json.loads(self.monthly_history) if self.monthly_history else {}
        except Exception:
            return {}

    def set_month_status(self, month_key, status, year=None):
        month = int(month_key)
        year = year or datetime.now().year
        payment = MonthlyPayment.query.filter_by(user_id=self.id, year=year, month=month).first()
        if not payment:
            payment = MonthlyPayment(user_id=self.id, year=year, month=month,
                                     amount=self.get_numeric_price(year, month))
            db.session.add(payment)
        payment.status = status
        payment.paid_at = datetime.utcnow() if status == 'pago' else None
        hist = self.get_month_history_dict() if year == datetime.now().year else {}
        hist[f'{month:02d}'] = status
        self.monthly_history = json.dumps(hist)
        statuses = [p.status for p in self.payments if p.year == year and p is not payment] + [status]
        self.payment_status = 'Pendente' if 'atrasado' in statuses else 'Em Dia'

    def get_month_schedule(self, current_month=None, year=None):
        today = datetime.now()
        current_month = current_month or today.month
        year = year or today.year
        start = self.start_month if self.start_month and self.start_month <= 12 else 1
        months = []
        month_names = {
            1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
            7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
        }
        hist = self.get_month_history_dict() if year == datetime.now().year else {}
        persisted_payments = {p.month: p for p in self.payments if p.year == year}

        for m in range(start, 13):
            m_str = f"{m:02d}"
            payment_obj = persisted_payments.get(m)
            if payment_obj:
                status = payment_obj.status
                amount = float(payment_obj.amount)
            elif self.is_fee_exempt_for(year, m):
                status = 'isento'
                amount = 0.0
            else:
                amount = self.get_numeric_price(year, m)
                if m_str in hist:
                    status = hist[m_str]
                elif m < current_month:
                    status = 'pago'
                elif m == current_month:
                    status = 'pago' if self.payment_status == 'Em Dia' else 'atrasado'
                else:
                    status = 'futuro'

            if m <= current_month:
                due_day_val = self.original_due_day
            else:
                due_day_val = int(self.due_date) if self.due_date and self.due_date.isdigit() else 15

            due_day_str = f"{due_day_val:02d}"
            months.append({
                'month': m_str,
                'name': month_names.get(m, ''),
                'due_day': due_day_str,
                'status': status,
                'amount': amount,
                'formatted_amount': f"R$ {amount:.2f}".replace('.', ',')
            })
        return months

    def get_numeric_price(self, year=None, month=None):
        if self.is_fee_exempt_for(year, month):
            return 0.0
        return self.get_plan_price()

    def get_plan_price(self):
        match = re.search(r'R\$\s*([\d\.,]+)', self.plan)
        if match:
            val_str = match.group(1).replace('.', '').replace(',', '.')
            try:
                base_price = float(val_str)
                if self.sponsored_dependents:
                    plan_name = self.plan.split('•')[0].split('—')[0].strip()
                    plan_record = Plan.query.filter(db.func.lower(Plan.name) == plan_name.casefold()).first()
                    if plan_record and plan_record.discount_percent:
                        return round(base_price * (1 - float(plan_record.discount_percent) / 100), 2)
                return base_price
            except ValueError:
                return 120.0
        return 120.0

    def get_overdue_details(self, current_month=None):
        schedule = self.get_month_schedule(current_month)
        overdue_months = [m for m in schedule if m['status'] == 'atrasado']
        overdue_count = len(overdue_months)
        
        current_date = datetime.now()
        if overdue_count == 0 and self.payment_status == 'Pendente' and not self.is_fee_exempt_for(
            current_date.year, current_month or current_date.month
        ):
            overdue_count = 1
            month = current_month or datetime.now().month
            overdue_months = [{'month': f'{month:02d}', 'name': '', 'status': 'atrasado'}]

        unit_price = self.get_plan_price()
        total_debt = overdue_count * unit_price
        months_str = ", ".join([f"{m['month']}/{m['name']}" for m in overdue_months]) if overdue_months else "08/Ago"

        return {
            'count': overdue_count,
            'total_debt': total_debt,
            'unit_price': unit_price,
            'months_str': months_str
        }

    def get_whatsapp_billing_link(self):
        clean_ddd = ''.join(c for c in self.ddd if c.isdigit())
        clean_phone = ''.join(c for c in self.phone if c.isdigit())
        full_number = f"55{clean_ddd}{clean_phone}"

        details = self.get_overdue_details()
        overdue_count = details['count']
        total_debt = details['total_debt']
        months_str = details['months_str']
        unit_price = details['unit_price']

        plan_simple = self.plan.split('—')[0].replace('⚡', '').replace('🔥', '').replace('👨‍👩‍👧', '').strip()
        first_name = self.name.split(' ')[0]

        # MENSAGEM DIRETA, CLARA E SEM SÍMBOLOS DE ERRO DE ENCODING
        if overdue_count > 1:
            msg = (
                f"Olá, {first_name}!\n\n"
                f"Segue o resumo do seu débito no BJ Sports Centro de Treinamento:\n\n"
                f"*Plano:* {plan_simple}\n"
                f"*Vencimento:* Todo Dia {self.due_date}\n"
                f"*Mensalidades Pendentes:* {overdue_count} meses ({months_str})\n"
                f"*Valor Total Devido:* R$ {total_debt:.2f}\n\n"
                f"Chave PIX para quitação:\n"
                f"*PIX:* (83) 99652-7997 (Mestre Bolivar)\n\n"
                f"Caso já tenha efetuado o pagamento, favor enviar o comprovante. OSS!"
            )
        else:
            msg = (
                f"Olá, {first_name}!\n\n"
                f"Segue o lembrete da sua mensalidade no BJ Sports Centro de Treinamento:\n\n"
                f"*Plano:* {plan_simple}\n"
                f"*Vencimento:* Dia {self.due_date}\n"
                f"*Valor:* R$ {unit_price:.2f}\n"
                f"*Status:* Pendente\n\n"
                f"Chave PIX para pagamento:\n"
                f"*PIX:* (83) 99652-7997 (Mestre Bolivar)\n\n"
                f"Favor enviar o comprovante assim que realizar o pagamento. OSS!"
            )

        return f"https://wa.me/{full_number}?text={urllib.parse.quote(msg)}"

class ContractAcceptance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    membership_terms_version = db.Column(db.String(20), nullable=False)
    privacy_notice_version = db.Column(db.String(20), nullable=False)
    image_consent_scope = db.Column(db.String(20), nullable=False, default='none')
    source = db.Column(db.String(30), nullable=False, default='account')
    accepted_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('contract_acceptances', lazy=True, cascade='all, delete-orphan'))

class Plan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    price = db.Column(db.String(50), nullable=False)
    price_ter_qui = db.Column(db.String(50), nullable=True)
    price_seg_qua_sex = db.Column(db.String(50), nullable=True)
    price_all_days = db.Column(db.String(50), nullable=True)
    discount_percent = db.Column(db.Numeric(5, 2), nullable=False, default=0)
    selection_count = db.Column(db.Integer, nullable=True)
    shared_type = db.Column(db.String(20), nullable=True)
    force_all_days = db.Column(db.Boolean, nullable=True)
    sub = db.Column(db.String(200), nullable=True)
    features = db.Column(db.Text, nullable=True)
    is_featured = db.Column(db.Boolean, default=False)
    modality = db.Column(db.String(150), nullable=True) # e.g. "Jiu-Jitsu, Boxe, Muay Thai, MMA"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_modalities(self):
        if self.modality:
            return [m.strip() for m in self.modality.split(',') if m.strip()]
        text = f"{self.name} {self.category} {self.sub or ''} {self.features or ''}".lower()
        if 'passe livre' in text or 'casal' in text or 'família' in text or 'familia' in text or 'todas' in text or 'qualquer' in text:
            return ['Jiu-Jitsu', 'Boxe', 'Muay Thai', 'MMA']
        if 'combo + 1' in text or 'combo 1' in text or 'combo+1' in text:
            return ['Jiu-Jitsu', 'Boxe', 'Muay Thai']
        if 'combo + 2' in text or 'combo 2' in text or 'combo+2' in text:
            return ['Jiu-Jitsu', 'Boxe', 'Muay Thai', 'MMA']
        mods = []
        if 'jiu-jitsu' in text or 'bjj' in text:
            mods.append('Jiu-Jitsu')
        if 'boxe' in text:
            mods.append('Boxe')
        if 'muay' in text:
            mods.append('Muay Thai')
        if 'mma' in text:
            mods.append('MMA')
        if not mods:
            mods = ['Jiu-Jitsu']
        return mods

    def get_price_for_schedule(self, schedule):
        if self.get_shared_type() in {'couple', 'family'} or self.price == 'Calculado via Desconto':
            if self.discount_percent and self.discount_percent > 0:
                return f"{int(self.discount_percent)}% OFF"
            return "Calculado via Desconto"
        prices = {
            'ter-qui': self.price_ter_qui,
            'seg-qua-sex': self.price_seg_qua_sex,
            'todos': self.price_all_days,
        }
        return prices.get(schedule) or self.price

    def get_selection_count(self):
        if self.selection_count is not None:
            return self.selection_count
        normalized = self.name.casefold()
        return 2 if 'combo + 1' in normalized else (3 if 'combo + 2' in normalized else 0)

    def get_shared_type(self):
        if self.shared_type in {'couple', 'family'}:
            return self.shared_type
        normalized = self.name.casefold()
        return 'couple' if 'casal' in normalized else ('family' if 'família' in normalized or 'familia' in normalized else 'none')

    def requires_all_days(self):
        return self.force_all_days if self.force_all_days is not None else self.category != 'Planos Individuais'

class Location(db.Model):
    __tablename__ = 'locations'
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    subtitle = db.Column(db.String(255), nullable=True)
    state = db.Column(db.String(10), nullable=False, default='PB')
    city = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    professor_name = db.Column(db.String(120), nullable=True)
    professor_title = db.Column(db.String(120), nullable=True)
    professor_bio = db.Column(db.Text, nullable=True)
    professor_phone = db.Column(db.String(30), nullable=True)
    professor_phone_formatted = db.Column(db.String(30), nullable=True)
    professor_photo = db.Column(db.String(255), nullable=True)
    professor_instagram = db.Column(db.String(100), nullable=True)
    logo_ct = db.Column(db.String(255), nullable=True)
    badge_color = db.Column(db.String(30), default='bg-gold')
    modalities_json = db.Column(db.Text, nullable=True, default='[]')
    maps_link = db.Column(db.String(500), nullable=True)
    description = db.Column(db.Text, nullable=True)
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login_or_name = db.Column(db.String(120), nullable=False)
    cpf3 = db.Column(db.String(3), nullable=True)
    modality = db.Column(db.String(100), nullable=False)
    shift_time = db.Column(db.String(150), nullable=False)
    class_group_id = db.Column(db.Integer, db.ForeignKey('class_group.id'), index=True)
    class_date = db.Column(db.Date, index=True)
    class_time = db.Column(db.String(5))
    is_experimental = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    class_group = db.relationship('ClassGroup', backref=db.backref('bookings', lazy=True))

class MonthlyPayment(db.Model):
    __table_args__ = (db.UniqueConstraint('user_id', 'year', 'month', name='uq_payment_period'),)
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='futuro')
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    paid_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('payments', lazy=True, cascade='all, delete-orphan'))


def change_user_due_date_with_proration(user, new_due_date):
    """Altera o vencimento e acrescenta o proporcional de dias extras obrigatoriamente no MÊS SEGUINTE."""
    try:
        new_day = int(new_due_date)
        if not (1 <= new_day <= 28):
            raise ValueError
    except (ValueError, TypeError):
        raise ValueError('Dia de vencimento inválido (deve ser entre 1 e 28).')

    old_day = int(user.due_date) if user.due_date and user.due_date.isdigit() else 15
    if not user.initial_due_date:
        user.initial_due_date = str(old_day)
    if str(new_day) == str(user.due_date):
        return {'days': 0, 'amount': Decimal('0.00'), 'payment': None}

    if new_day >= old_day:
        extra_days = new_day - old_day
    else:
        extra_days = (30 - old_day) + new_day

    user.due_date = str(new_day)
    if not extra_days or user.is_fee_exempt_for():
        return {'days': extra_days, 'amount': Decimal('0.00'), 'payment': None}

    now = datetime.now()
    # A alteração de vencimento reflete obrigatoriamente no MÊS SEGUINTE (target_month = now.month + 1)
    target_month = now.month + 1
    target_year = now.year
    if target_month == 13:
        target_month = 1
        target_year += 1

    baseline_amount = Decimal(str(user.get_numeric_price(target_year, target_month)))
    proportional_amount = (baseline_amount * Decimal(extra_days) / Decimal(30)).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP
    )

    # Reseta faturas abertas de outros meses para o valor base normal do plano (mantendo o mês atual intacto)
    other_unpaid_payments = MonthlyPayment.query.filter(
        MonthlyPayment.user_id == user.id,
        MonthlyPayment.status != 'pago'
    ).all()

    for p in other_unpaid_payments:
        if (p.year, p.month) != (target_year, target_month):
            p.amount = Decimal(str(user.get_numeric_price(p.year, p.month)))

    # Atualiza ou cria a fatura do MÊS SEGUINTE com o valor base + proporcional
    target_payment = MonthlyPayment.query.filter_by(
        user_id=user.id, year=target_year, month=target_month
    ).first()

    if not target_payment:
        target_payment = MonthlyPayment(
            user_id=user.id, year=target_year, month=target_month,
            status='futuro',
            amount=baseline_amount + proportional_amount
        )
        db.session.add(target_payment)
    else:
        target_payment.amount = baseline_amount + proportional_amount

    return {'days': extra_days, 'amount': proportional_amount, 'payment': target_payment}

class MonthlyFeeExemption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    start_year = db.Column(db.Integer, nullable=False)
    start_month = db.Column(db.Integer, nullable=False)
    end_year = db.Column(db.Integer)
    end_month = db.Column(db.Integer)
    granted_by_username = db.Column(db.String(80), nullable=False)
    granted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    revoked_by_username = db.Column(db.String(80))
    revoked_at = db.Column(db.DateTime)
    user = db.relationship('User', backref=db.backref(
        'fee_exemptions', lazy=True, cascade='all, delete-orphan', order_by='MonthlyFeeExemption.start_year'
    ))

    def covers(self, year, month):
        period_key = year * 100 + month
        start_key = self.start_year * 100 + self.start_month
        end_key = self.end_year * 100 + self.end_month if self.end_year and self.end_month else None
        return period_key >= start_key and (end_key is None or period_key < end_key)

class ClassGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    modality = db.Column(db.String(40), nullable=False)
    audience = db.Column(db.String(30), nullable=False, default='Adulto')
    schedules_json = db.Column(db.Text, nullable=False, default='[]')
    instructor = db.Column(db.String(120), nullable=False, default='Mestre Bolivar')
    responsible_monitor_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    capacity = db.Column(db.Integer, nullable=False, default=20)
    waiting = db.Column(db.Integer, nullable=False, default=0)
    duration_minutes = db.Column(db.Integer, nullable=False, default=60)
    status = db.Column(db.String(20), nullable=False, default='ativa')
    publish_public = db.Column(db.Boolean, nullable=False, default=True)
    location_slug = db.Column(db.String(80), nullable=False, default='cajazeiras-sede')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    responsible_monitor = db.relationship('User', foreign_keys=[responsible_monitor_id])

    @property
    def location_info(self):
        locs = get_locations_dict()
        slug = self.location_slug or 'cajazeiras-sede'
        return locs.get(slug, locs.get('cajazeiras-sede', {'name': 'Cajazeiras (Sede Matriz)', 'badge_color': 'bg-green'}))

    @property
    def schedules(self):
        try:
            return json.loads(self.schedules_json) if self.schedules_json else []
        except (TypeError, ValueError):
            return []

    @schedules.setter
    def schedules(self, values):
        self.schedules_json = json.dumps(values, ensure_ascii=False)

    @property
    def weekly_sessions(self):
        total = 0
        for schedule in self.schedules:
            days_text, _, times_text = schedule.partition('•')
            total += len([item for item in days_text.split(',') if item.strip()]) * len(re.findall(r'\d{2}:\d{2}', times_text))
        return total

    @property
    def enrolled(self):
        return sum(1 for enrollment in self.enrollments if enrollment.active)

class ClassEnrollment(db.Model):
    __table_args__ = (db.UniqueConstraint('user_id', 'class_group_id', name='uq_user_class_group'),)
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    class_group_id = db.Column(db.Integer, db.ForeignKey('class_group.id'), nullable=False, index=True)
    active = db.Column(db.Boolean, nullable=False, default=True)
    is_demo = db.Column(db.Boolean, nullable=False, default=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('class_enrollments', lazy=True, cascade='all, delete-orphan'))
    class_group = db.relationship('ClassGroup', backref=db.backref('enrollments', lazy=True, cascade='all, delete-orphan'))

class SpecialClassEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    event_date = db.Column(db.Date, nullable=False, index=True)
    start_time = db.Column(db.String(5), nullable=False)
    end_time = db.Column(db.String(5), nullable=False)
    modality = db.Column(db.String(40), nullable=False, default='Treino especial')
    notes = db.Column(db.String(300))
    created_by_username = db.Column(db.String(80), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='agendado')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PushSubscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    endpoint = db.Column(db.Text, unique=True, nullable=False)
    p256dh = db.Column(db.String(180), nullable=False)
    auth = db.Column(db.String(100), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    last_occurrence_key = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('push_subscriptions', lazy=True, cascade='all, delete-orphan'))

class GraduationRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    previous_belt_color = db.Column(db.String(20), nullable=False)
    previous_belt_degree = db.Column(db.Integer, nullable=False, default=0)
    new_belt_color = db.Column(db.String(20), nullable=False)
    new_belt_degree = db.Column(db.Integer, nullable=False, default=0)
    graduation_date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.String(300))
    updated_by_username = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('graduation_records', lazy=True, cascade='all, delete-orphan'))

class InternalChampionship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    modality = db.Column(db.String(40), nullable=False)
    event_date = db.Column(db.Date, nullable=False, index=True)
    registration_deadline = db.Column(db.Date, nullable=False)
    location = db.Column(db.String(160), nullable=False)
    max_participants = db.Column(db.Integer, nullable=False, default=40)
    description = db.Column(db.String(500))
    status = db.Column(db.String(30), nullable=False, default='inscricoes_abertas')
    created_by_username = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def registered_count(self):
        return sum(1 for registration in self.registrations if registration.status == 'inscrito')

class ChampionshipRegistration(db.Model):
    __table_args__ = (db.UniqueConstraint('championship_id', 'user_id', name='uq_championship_user'),)
    id = db.Column(db.Integer, primary_key=True)
    championship_id = db.Column(db.Integer, db.ForeignKey('internal_championship.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    weight = db.Column(db.Float, nullable=False)
    age_division = db.Column(db.String(30), nullable=False)
    belt_color_snapshot = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='inscrito')
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    championship = db.relationship('InternalChampionship', backref=db.backref('registrations', lazy=True, cascade='all, delete-orphan'))
    user = db.relationship('User', backref=db.backref('championship_registrations', lazy=True, cascade='all, delete-orphan'))

class ChampionshipWeightDivision(db.Model):
    __table_args__ = (db.UniqueConstraint('gender', 'category', name='uq_weight_gender_category'),)
    id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.String(20), nullable=False, index=True)
    category = db.Column(db.String(40), nullable=False)
    pre_mirim = db.Column(db.String(40), nullable=False, default='')
    mirim = db.Column(db.String(40), nullable=False, default='')
    infantil = db.Column(db.String(40), nullable=False, default='')
    infanto = db.Column(db.String(40), nullable=False, default='')
    juvenil = db.Column(db.String(40), nullable=False, default='')
    adulto_master = db.Column(db.String(40), nullable=False, default='')
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    updated_by_username = db.Column(db.String(80))
    updated_at = db.Column(db.DateTime)

class ChampionshipWeightRevision(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    division_id = db.Column(db.Integer, db.ForeignKey('championship_weight_division.id'), nullable=False, index=True)
    changes_json = db.Column(db.Text, nullable=False)
    updated_by_username = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    division = db.relationship('ChampionshipWeightDivision', backref=db.backref('revisions', lazy=True, cascade='all, delete-orphan'))

class ChampionshipMatch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    championship_id = db.Column(db.Integer, db.ForeignKey('internal_championship.id'), nullable=False, index=True)
    red_competitor = db.Column(db.String(120), nullable=False)
    blue_competitor = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(120), nullable=False)
    mat_area = db.Column(db.String(40), nullable=False, default='Área 1')
    duration_seconds = db.Column(db.Integer, nullable=False, default=300)
    remaining_seconds = db.Column(db.Integer, nullable=False, default=300)
    timer_running = db.Column(db.Boolean, nullable=False, default=False)
    timer_started_at = db.Column(db.DateTime)
    red_score = db.Column(db.Integer, nullable=False, default=0)
    blue_score = db.Column(db.Integer, nullable=False, default=0)
    red_advantages = db.Column(db.Integer, nullable=False, default=0)
    blue_advantages = db.Column(db.Integer, nullable=False, default=0)
    red_penalties = db.Column(db.Integer, nullable=False, default=0)
    blue_penalties = db.Column(db.Integer, nullable=False, default=0)
    penalty_limit = db.Column(db.Integer, nullable=False, default=4)
    status = db.Column(db.String(30), nullable=False, default='aguardando')
    winner_side = db.Column(db.String(10))
    updated_by_username = db.Column(db.String(80))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    championship = db.relationship('InternalChampionship', backref=db.backref('matches', lazy=True, cascade='all, delete-orphan'))

class ChampionshipScoreEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('championship_match.id'), nullable=False, index=True)
    side = db.Column(db.String(10), nullable=False)
    action_key = db.Column(db.String(40), nullable=False)
    label = db.Column(db.String(120), nullable=False)
    consequence = db.Column(db.String(160))
    before_state_json = db.Column(db.Text, nullable=False)
    created_by_username = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    undone_at = db.Column(db.DateTime)
    undone_by_username = db.Column(db.String(80))
    match = db.relationship('ChampionshipMatch', backref=db.backref('score_events', lazy=True, cascade='all, delete-orphan'))

class Attendance(db.Model):
    __table_args__ = (db.UniqueConstraint('user_id', 'training_date', name='uq_attendance_day'),)
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    class_group_id = db.Column(db.Integer, db.ForeignKey('class_group.id'), index=True)
    training_date = db.Column(db.Date, nullable=False, default=lambda: datetime.now().date())
    modality = db.Column(db.String(60), nullable=False, default='Treino')
    status = db.Column(db.String(20), nullable=False, default='pendente')
    confirmed_by_username = db.Column(db.String(80))
    confirmed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('attendances', lazy=True, cascade='all, delete-orphan'))
    class_group = db.relationship('ClassGroup', backref=db.backref('attendances', lazy=True))

def parse_class_schedules(raw_value):
    parts = re.split(r'\s*(?:/|\n|;)\s*', (raw_value or '').strip())
    return [part.strip() for part in parts if part.strip()]

CLASS_WEEKDAY_LOOKUP = {'Seg': 0, 'Ter': 1, 'Qua': 2, 'Qui': 3, 'Sex': 4, 'Sáb': 5, 'Dom': 6}
CHAMPIONSHIP_MATCH_DURATIONS = (2, 3, 4, 5, 6, 10)

def time_to_minutes(value):
    if not re.fullmatch(r'(?:[01]\d|2[0-3]):[0-5]\d', value or ''):
        raise ValueError('Horário inválido.')
    hours, minutes = (int(part) for part in value.split(':', 1))
    return hours * 60 + minutes

def minutes_to_time(value):
    return f'{value // 60:02d}:{value % 60:02d}'

def match_remaining_seconds(match, reference_time=None):
    remaining = match.remaining_seconds
    if match.timer_running and match.timer_started_at:
        reference_time = reference_time or datetime.utcnow()
        remaining -= max(0, int((reference_time - match.timer_started_at).total_seconds()))
    return max(0, remaining)

def class_occurrences_for_weekday(class_group, weekday):
    occurrences = []
    for schedule in class_group.schedules:
        days_text, _, times_text = schedule.partition('•')
        weekdays = [CLASS_WEEKDAY_LOOKUP.get(item.strip()) for item in days_text.split(',')]
        if weekday not in weekdays:
            continue
        for class_time in re.findall(r'\d{2}:\d{2}', times_text):
            start = time_to_minutes(class_time)
            occurrences.append({
                'start': start, 'end': start + class_group.duration_minutes,
                'start_time': class_time, 'end_time': minutes_to_time(start + class_group.duration_minutes),
                'name': class_group.name, 'modality': class_group.modality,
                'audience': class_group.audience, 'instructor': class_group.instructor,
                'status': class_group.status, 'special': False,
            })
    return occurrences

def active_groups_for_user(user_id):
    return [enrollment.class_group for enrollment in ClassEnrollment.query.filter_by(
        user_id=user_id, active=True,
    ).all() if enrollment.class_group and enrollment.class_group.publish_public]

def escape_ics(value):
    return str(value or '').replace('\\', '\\\\').replace(';', '\\;').replace(',', '\\,').replace('\n', '\\n')

def personal_calendar_ics(user):
    today = datetime.now().date()
    until = today + timedelta(days=366)
    day_codes = {0: 'MO', 1: 'TU', 2: 'WE', 3: 'TH', 4: 'FR', 5: 'SA', 6: 'SU'}
    lines = [
        'BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//BJ Sports//Minhas Turmas//PT-BR',
        'CALSCALE:GREGORIAN', 'METHOD:PUBLISH', 'X-WR-CALNAME:BJ Sports - Minhas Turmas',
        'X-WR-TIMEZONE:America/Recife',
    ]
    for class_group in active_groups_for_user(user.id):
        for schedule_index, schedule in enumerate(class_group.schedules):
            days_text, _, times_text = schedule.partition('•')
            weekdays = sorted({CLASS_WEEKDAY_LOOKUP[item.strip()] for item in days_text.split(',')
                               if item.strip() in CLASS_WEEKDAY_LOOKUP})
            if not weekdays:
                continue
            byday = ','.join(day_codes[item] for item in weekdays)
            for class_time in re.findall(r'\d{2}:\d{2}', times_text):
                start_minutes = time_to_minutes(class_time)
                days_until = min((weekday - today.weekday()) % 7 for weekday in weekdays)
                first_date = today + timedelta(days=days_until)
                start_value = f'{first_date:%Y%m%d}T{start_minutes // 60:02d}{start_minutes % 60:02d}00'
                end_minutes = start_minutes + class_group.duration_minutes
                end_value = f'{first_date:%Y%m%d}T{end_minutes // 60:02d}{end_minutes % 60:02d}00'
                lines.extend([
                    'BEGIN:VEVENT',
                    f'UID:bjsports-{user.id}-{class_group.id}-{schedule_index}-{class_time.replace(":", "")}@bjsports',
                    f'DTSTAMP:{datetime.utcnow():%Y%m%dT%H%M%SZ}',
                    f'DTSTART;TZID=America/Recife:{start_value}',
                    f'DTEND;TZID=America/Recife:{end_value}',
                    f'RRULE:FREQ=WEEKLY;BYDAY={byday};UNTIL={until:%Y%m%d}T235959Z',
                    f'SUMMARY:{escape_ics(class_group.name)}',
                    f'DESCRIPTION:{escape_ics(class_group.modality + " - " + class_group.audience)}',
                    f'LOCATION:{escape_ics("BJ Sports Centro de Treinamento")}',
                    'BEGIN:VALARM', 'TRIGGER:-PT60M', 'ACTION:DISPLAY',
                    f'DESCRIPTION:Lembrete: {escape_ics(class_group.name)} em 1 hora', 'END:VALARM',
                    'END:VEVENT',
                ])
    lines.append('END:VCALENDAR')
    return '\r\n'.join(lines) + '\r\n'

def push_configuration():
    private_key = os.getenv('VAPID_PRIVATE_KEY', '').strip()
    public_key = os.getenv('VAPID_PUBLIC_KEY', '').strip()
    subject = os.getenv('VAPID_SUBJECT', 'mailto:contato@bjsports.local').strip()
    return private_key, public_key, subject

def deliver_push(subscription, payload):
    private_key, public_key, subject = push_configuration()
    if not private_key or not public_key:
        raise RuntimeError('As chaves VAPID ainda não foram configuradas.')
    from pywebpush import webpush
    webpush(
        subscription_info={'endpoint': subscription.endpoint,
                           'keys': {'p256dh': subscription.p256dh, 'auth': subscription.auth}},
        data=json.dumps(payload, ensure_ascii=False),
        vapid_private_key=private_key,
        vapid_claims={'sub': subject},
    )

def ensure_db_schema_columns():
    try:
        with db.engine.connect() as conn:
            if db.engine.name == 'postgresql':
                conn.execute(db.text("ALTER TABLE class_group ADD COLUMN IF NOT EXISTS location_slug VARCHAR(80) DEFAULT 'cajazeiras-sede';"))
            else:
                try:
                    conn.execute(db.text("ALTER TABLE class_group ADD COLUMN location_slug VARCHAR(80) DEFAULT 'cajazeiras-sede';"))
                except Exception:
                    pass
            conn.commit()
    except Exception as exc:
        print(f"Column migration check note: {exc}")

def ensure_class_groups():
    ensure_db_schema_columns()
    if ClassGroup.query.count() == 0:
        for item in DEFAULT_CLASS_GROUPS:
            class_group = ClassGroup(
                name=item['name'], modality=item['modality'], audience=item['audience'],
                instructor=item['instructor'], capacity=item['capacity'], waiting=item['waiting'],
                duration_minutes=60, status=item['status'], publish_public=True,
            )
            class_group.schedules = item['schedules']
            db.session.add(class_group)
        db.session.commit()

def migrate_sqlite_to_postgres():
    if not app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgresql'):
        return
    sqlite_db_path = os.path.join(app.instance_path, 'user.db')
    if not os.path.exists(sqlite_db_path):
        return
    try:
        if User.query.count() > 0:
            return
    except Exception:
        pass

    import sqlite3
    print(f"Migrating data from SQLite ({sqlite_db_path}) to PostgreSQL...")
    try:
        sq_conn = sqlite3.connect(sqlite_db_path)
        sq_conn.row_factory = sqlite3.Row
        sq_cursor = sq_conn.cursor()

        sq_users = sq_cursor.execute("SELECT * FROM user").fetchall()
        for row in sq_users:
            u_dict = dict(row)
            if not User.query.filter_by(username=u_dict['username']).first():
                u = User()
                for key in u_dict:
                    if hasattr(u, key) and u_dict[key] is not None:
                        val = u_dict[key]
                        if isinstance(val, str) and ('_at' in key or 'date' in key):
                            try:
                                val = datetime.fromisoformat(val)
                            except Exception:
                                pass
                        setattr(u, key, val)
                db.session.add(u)
        db.session.commit()

        sq_plans = sq_cursor.execute("SELECT * FROM plan").fetchall()
        for row in sq_plans:
            p_dict = dict(row)
            if not Plan.query.filter_by(name=p_dict['name']).first():
                p = Plan()
                for key in p_dict:
                    if hasattr(p, key) and p_dict[key] is not None:
                        setattr(p, key, p_dict[key])
                db.session.add(p)
        db.session.commit()

        try:
            sq_groups = sq_cursor.execute("SELECT * FROM class_group").fetchall()
            for row in sq_groups:
                g_dict = dict(row)
                if not ClassGroup.query.filter_by(name=g_dict['name']).first():
                    cg = ClassGroup()
                    for key in g_dict:
                        if hasattr(cg, key) and g_dict[key] is not None:
                            setattr(cg, key, g_dict[key])
                    db.session.add(cg)
            db.session.commit()
        except Exception:
            pass

        sq_conn.close()
        print("Data migration from SQLite to PostgreSQL completed successfully!")
    except Exception as e:
        print("SQLite to PostgreSQL migration note:", e)

def ensure_schema_updates():
    try:
        from sqlalchemy import inspect, text
        inspector = inspect(db.engine)
        columns = [c['name'] for c in inspector.get_columns('plan')]
        if 'modality' not in columns:
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE plan ADD COLUMN modality VARCHAR(150)'))
                conn.commit()
        for column_name in ('price_ter_qui', 'price_seg_qua_sex', 'price_all_days'):
            if column_name not in columns:
                with db.engine.connect() as conn:
                    conn.execute(text(f'ALTER TABLE plan ADD COLUMN {column_name} VARCHAR(50)'))
                    conn.commit()
        if 'discount_percent' not in columns:
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE plan ADD COLUMN discount_percent NUMERIC(5,2) NOT NULL DEFAULT 0'))
                conn.commit()
        for column_name, definition in (
            ('selection_count', 'INTEGER'), ('shared_type', 'VARCHAR(20)'), ('force_all_days', 'BOOLEAN')
        ):
            if column_name not in columns:
                with db.engine.connect() as conn:
                    conn.execute(text(f'ALTER TABLE plan ADD COLUMN {column_name} {definition}'))
                    conn.commit()
    except Exception as e:
        print('Schema migration note:', e)

def ensure_mma_classes_and_plans():
    ensure_schema_updates()
    old_group = ClassGroup.query.filter_by(name='Jiu-Jitsu Almoço').first()
    if old_group:
        old_group.name = 'Jiu-Jitsu / Meio dia'
        db.session.commit()

    mma_plan = Plan.query.filter(Plan.name.like('%MMA%')).first()
    if not mma_plan:
        p_mma = Plan(
            name='🥊 Plano MMA (Profissional & Amador)',
            category='Planos Individuais',
            price='R$ 130,00/mês',
            sub='MMA Profissional (Seg, Qua, Sex • 11h30) e Iniciantes (Ter, Qui • 18h00)',
            features='Treinos de MMA Profissional (Seg, Qua, Sex 11h30);Treinos de MMA Amador / Iniciantes (Ter, Qui 18h00);Acompanhamento do Mestre Bolivar;Preparação física e técnica completa',
            is_featured=False
        )
        db.session.add(p_mma)
        db.session.commit()

    boxe_plan = Plan.query.filter(Plan.name.like('%Boxe%')).first()
    if not boxe_plan:
        p_boxe = Plan(
            name='🥊 Plano Boxe Tradicional',
            category='Planos Individuais',
            price='R$ 100,00/mês',
            sub='Treinos de Boxe Matinal (06:00h) e Noturno (19:00h)',
            features='Aulas de Boxe Tradicional;Técnica e condicionamento físico;Matinal (Seg, Qua, Sex) e Noturno (Ter, Qui)',
            is_featured=False
        )
        db.session.add(p_boxe)

    muay_plan = Plan.query.filter(Plan.name.like('%Muay Thai%')).first()
    if not muay_plan:
        p_muay = Plan(
            name='⚔️ Plano Muay Thai',
            category='Planos Individuais',
            price='R$ 100,00/mês',
            sub='Treinos de Muay Thai Adulto e Kids',
            features='Aulas de Muay Thai Adulto e Kids;Fundamentos e condicionamento completo;Turmas de manhã, tarde e noite',
            is_featured=False
        )
        db.session.add(p_muay)

    db.session.commit()

    combo1_plan = Plan.query.filter(Plan.name.ilike('%Combo%1%')).first()
    if not combo1_plan:
        p_combo1 = Plan(
            name='⚡ Plano Combo + 1',
            category='Planos Promocionais & Família',
            price='R$ 150,00/mês',
            sub='Escolha 2 modalidades para praticar na academia',
            features='Pratique 2 modalidades à sua escolha (Jiu-Jitsu, Boxe, Muay Thai ou MMA);Treinos em dias e turnos alternados;Acompanhamento técnico integrado;Economia garantida no pacote mensal',
            is_featured=True
        )
        db.session.add(p_combo1)

    combo2_plan = Plan.query.filter(Plan.name.ilike('%Combo%2%')).first()
    if not combo2_plan:
        p_combo2 = Plan(
            name='🔥 Plano Combo + 2',
            category='Planos Promocionais & Família',
            price='R$ 180,00/mês',
            sub='Escolha 3 modalidades para praticar na academia',
            features='Pratique 3 modalidades à sua escolha no centro de treinamento;Treinos intensivos de Jiu-Jitsu, Boxe, Muay Thai ou MMA;Evolução técnica e física multifuncional;Acesso flexível a múltiplos horários',
            is_featured=False
        )
        db.session.add(p_combo2)

    db.session.commit()

    pro_group = ClassGroup.query.filter_by(name='MMA Profissional').first()
    if not pro_group:
        cg_pro = ClassGroup(
            name='MMA Profissional', modality='MMA', audience='Profissional',
            instructor='Mestre Bolivar', capacity=20, waiting=0,
            duration_minutes=60, status='ativa', publish_public=True
        )
        cg_pro.schedules = ['Seg, Qua, Sex • 11:30']
        db.session.add(cg_pro)

    init_group = ClassGroup.query.filter_by(name='MMA Amador / Iniciantes').first()
    if not init_group:
        cg_init = ClassGroup(
            name='MMA Amador / Iniciantes', modality='MMA', audience='Iniciantes',
            instructor='Mestre Bolivar', capacity=20, waiting=0,
            duration_minutes=60, status='ativa', publish_public=True
        )
        cg_init.schedules = ['Ter, Qui • 18:00']
        db.session.add(cg_init)

    db.session.commit()

def ensure_championship_weights():
    if ChampionshipWeightDivision.query.count() > 0:
        return
    for gender, rows in CHAMPIONSHIP_WEIGHT_SEED.items():
        for sort_order, values in enumerate(rows):
            category, pre_mirim, mirim, infantil, infanto, juvenil, adulto_master = values
            db.session.add(ChampionshipWeightDivision(
                gender=gender, category=category, pre_mirim=pre_mirim, mirim=mirim,
                infantil=infantil, infanto=infanto, juvenil=juvenil,
                adulto_master=adulto_master, sort_order=sort_order,
            ))
    db.session.commit()

def ensure_default_accounts():
    bolivar = User.query.filter_by(username='bolivar').first()
    if not bolivar:
        bolivar = User(
            username='bolivar', name='Mestre Bolivar', cpf='000.000.001-00',
            ddd='83', phone='996527997', plan='Passe Livre — R$ 120,00/mês',
            due_date='5', start_month=1, role='instrutor', payment_status='Em Dia'
        )
        bolivar.set_password('bolivar')
        db.session.add(bolivar)
    elif bolivar.role != 'instrutor':
        bolivar.role = 'instrutor'

    db.session.commit()

with app.app_context():
    try:
        db.create_all()
    except Exception:
        db.session.rollback()

    # Migração compatível com a base SQLite já existente.
    # Os workers do Gunicorn importam este módulo em paralelo. No PostgreSQL,
    # serializamos as alterações de esquema para impedir DDL concorrente.
    if db.engine.dialect.name == 'postgresql':
        db.session.execute(text('SELECT pg_advisory_xact_lock(42457001)'))
    user_columns = {column['name'] for column in inspect(db.engine).get_columns('user')}
    if 'initial_due_date' not in user_columns:
        db.session.execute(text('ALTER TABLE "user" ADD COLUMN initial_due_date VARCHAR(10)'))
    if 'belt_color' not in user_columns:
        db.session.execute(text('ALTER TABLE "user" ADD COLUMN belt_color VARCHAR(20) NOT NULL DEFAULT \'branca\''))
    if 'belt_degree' not in user_columns:
        db.session.execute(text('ALTER TABLE "user" ADD COLUMN belt_degree INTEGER NOT NULL DEFAULT 0'))
    if 'monthly_fee_exempt' not in user_columns:
        db.session.execute(text('ALTER TABLE "user" ADD COLUMN monthly_fee_exempt BOOLEAN NOT NULL DEFAULT 0'))
    if 'sponsor_id' not in user_columns:
        db.session.execute(text('ALTER TABLE "user" ADD COLUMN sponsor_id INTEGER REFERENCES "user"(id)'))
        db.session.execute(text('CREATE INDEX IF NOT EXISTS ix_user_sponsor_id ON "user" (sponsor_id)'))
    if 'sponsored_previous_plan' not in user_columns:
        db.session.execute(text('ALTER TABLE "user" ADD COLUMN sponsored_previous_plan VARCHAR(150)'))
    if 'sponsored_previous_modalities' not in user_columns:
        db.session.execute(text('ALTER TABLE "user" ADD COLUMN sponsored_previous_modalities VARCHAR(250)'))
    if 'sponsor_started_at' not in user_columns:
        db.session.execute(text('ALTER TABLE "user" ADD COLUMN sponsor_started_at TIMESTAMP'))
    if 'fee_exempted_by_username' not in user_columns:
        db.session.execute(text('ALTER TABLE "user" ADD COLUMN fee_exempted_by_username VARCHAR(80)'))
    if 'fee_exempted_at' not in user_columns:
        db.session.execute(text('ALTER TABLE "user" ADD COLUMN fee_exempted_at DATETIME'))
    if 'email' not in user_columns:
        db.session.execute(text('ALTER TABLE "user" ADD COLUMN email VARCHAR(254)'))
    if 'sex' not in user_columns:
        db.session.execute(text("ALTER TABLE \"user\" ADD COLUMN sex VARCHAR(20) NOT NULL DEFAULT 'prefer_not'"))
    db.session.execute(text('CREATE UNIQUE INDEX IF NOT EXISTS ix_user_email_unique ON "user" (email)'))
    if 'membership_terms_version' not in user_columns:
        db.session.execute(text('ALTER TABLE "user" ADD COLUMN membership_terms_version VARCHAR(20)'))
    if 'membership_terms_accepted_at' not in user_columns:
        db.session.execute(text('ALTER TABLE "user" ADD COLUMN membership_terms_accepted_at DATETIME'))
    if 'privacy_notice_version' not in user_columns:
        db.session.execute(text('ALTER TABLE "user" ADD COLUMN privacy_notice_version VARCHAR(20)'))
    if 'privacy_notice_accepted_at' not in user_columns:
        db.session.execute(text('ALTER TABLE "user" ADD COLUMN privacy_notice_accepted_at DATETIME'))
    if 'image_use_consent' not in user_columns:
        db.session.execute(text('ALTER TABLE "user" ADD COLUMN image_use_consent BOOLEAN NOT NULL DEFAULT 0'))
    if 'image_use_consent_at' not in user_columns:
        db.session.execute(text('ALTER TABLE "user" ADD COLUMN image_use_consent_at DATETIME'))
    if 'image_consent_scope' not in user_columns:
        db.session.execute(text("ALTER TABLE \"user\" ADD COLUMN image_consent_scope VARCHAR(20) NOT NULL DEFAULT 'none'"))
    if 'image_consent_guardian_name' not in user_columns:
        db.session.execute(text('ALTER TABLE "user" ADD COLUMN image_consent_guardian_name VARCHAR(120)'))
    if 'image_consent_guardian_cpf' not in user_columns:
        db.session.execute(text('ALTER TABLE "user" ADD COLUMN image_consent_guardian_cpf VARCHAR(14)'))
    if 'image_consent_guardian_relationship' not in user_columns:
        db.session.execute(text('ALTER TABLE "user" ADD COLUMN image_consent_guardian_relationship VARCHAR(30)'))
    if 'medical_restriction' not in user_columns:
        db.session.execute(text('ALTER TABLE "user" ADD COLUMN medical_restriction VARCHAR(250)'))
    if 'is_experimental' not in user_columns:
        db.session.execute(text('ALTER TABLE "user" ADD COLUMN is_experimental BOOLEAN NOT NULL DEFAULT FALSE'))
    if 'selected_modalities' not in user_columns:
        db.session.execute(text('ALTER TABLE "user" ADD COLUMN selected_modalities VARCHAR(250)'))
    if 'birth_date' not in user_columns:
        birth_date_sql = ('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS birth_date DATE'
                          if db.engine.dialect.name == 'postgresql'
                          else 'ALTER TABLE "user" ADD COLUMN birth_date DATE')
        db.session.execute(text(birth_date_sql))
    if 'must_change_password' not in user_columns:
        db.session.execute(text('ALTER TABLE "user" ADD COLUMN must_change_password BOOLEAN NOT NULL DEFAULT FALSE'))
    if 'password_reset_by_username' not in user_columns:
        db.session.execute(text('ALTER TABLE "user" ADD COLUMN password_reset_by_username VARCHAR(80)'))
    if 'password_reset_at' not in user_columns:
        db.session.execute(text('ALTER TABLE "user" ADD COLUMN password_reset_at TIMESTAMP'))
    match_columns = {column['name'] for column in inspect(db.engine).get_columns('championship_match')}
    if 'penalty_limit' not in match_columns:
        db.session.execute(text('ALTER TABLE championship_match ADD COLUMN penalty_limit INTEGER NOT NULL DEFAULT 4'))
    attendance_columns = {column['name'] for column in inspect(db.engine).get_columns('attendance')}
    if 'status' not in attendance_columns:
        db.session.execute(text("ALTER TABLE attendance ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'confirmado'"))
    if 'modality' not in attendance_columns:
        db.session.execute(text("ALTER TABLE attendance ADD COLUMN modality VARCHAR(60) NOT NULL DEFAULT 'Treino'"))
    if 'confirmed_by_username' not in attendance_columns:
        db.session.execute(text('ALTER TABLE attendance ADD COLUMN confirmed_by_username VARCHAR(80)'))
    if 'confirmed_at' not in attendance_columns:
        db.session.execute(text('ALTER TABLE attendance ADD COLUMN confirmed_at DATETIME'))
    if 'class_group_id' not in attendance_columns:
        db.session.execute(text('ALTER TABLE attendance ADD COLUMN class_group_id INTEGER REFERENCES class_group(id)'))
    booking_columns = {column['name'] for column in inspect(db.engine).get_columns('booking')}
    if 'class_group_id' not in booking_columns:
        db.session.execute(text('ALTER TABLE booking ADD COLUMN class_group_id INTEGER REFERENCES class_group(id)'))
        db.session.execute(text('CREATE INDEX IF NOT EXISTS ix_booking_class_group_id ON booking (class_group_id)'))
    if 'class_date' not in booking_columns:
        db.session.execute(text('ALTER TABLE booking ADD COLUMN class_date DATE'))
        db.session.execute(text('CREATE INDEX IF NOT EXISTS ix_booking_class_date ON booking (class_date)'))
    if 'class_time' not in booking_columns:
        db.session.execute(text('ALTER TABLE booking ADD COLUMN class_time VARCHAR(5)'))
    class_group_columns = {column['name'] for column in inspect(db.engine).get_columns('class_group')}
    if 'responsible_monitor_id' not in class_group_columns:
        db.session.execute(text('ALTER TABLE class_group ADD COLUMN responsible_monitor_id INTEGER REFERENCES "user"(id)'))
        db.session.execute(text('CREATE INDEX IF NOT EXISTS ix_class_group_responsible_monitor_id ON class_group (responsible_monitor_id)'))
    db.session.commit()
    migrate_sqlite_to_postgres()

    # Converte isenções legadas sem período em uma vigência iniciada na competência atual.
    migration_date = datetime.now()
    for exempt_user in User.query.filter_by(monthly_fee_exempt=True).all():
        if not any(item.end_year is None for item in exempt_user.fee_exemptions):
            db.session.add(MonthlyFeeExemption(
                user_id=exempt_user.id,
                start_year=migration_date.year,
                start_month=migration_date.month,
                granted_by_username=exempt_user.fee_exempted_by_username or 'migração',
                granted_at=exempt_user.fee_exempted_at or datetime.utcnow(),
            ))
    db.session.commit()

    # Converte uma única vez o histórico JSON legado em competências anuais.
    if MonthlyPayment.query.count() == 0:
        migration_year = datetime.now().year
        for legacy_user in User.query.all():
            for legacy_month, legacy_status in legacy_user.get_month_history_dict().items():
                if legacy_month.isdigit() and legacy_status in {'pago', 'atrasado', 'futuro'}:
                    db.session.add(MonthlyPayment(
                        user_id=legacy_user.id, year=migration_year, month=int(legacy_month),
                        # O valor histórico pertence à competência registrada. A
                        # isenção atual não pode zerar pagamentos ou débitos
                        # anteriores durante a migração do formato legado.
                        status=legacy_status, amount=legacy_user.get_plan_price(),
                        paid_at=datetime.utcnow() if legacy_status == 'pago' else None
                    ))
        db.session.commit()
    
    ensure_schema_updates()
    if not Plan.query.first():
        p1 = Plan(name='⚡ Plano Passe Livre', category='Planos Individuais', price='R$ 120,00/mês', sub='Acesso total a todas as modalidades e horários', features='Liberdade de treinar todos os dias;Acesso aos treinos da manhã, tarde e noite;Acompanhamento individual de evolução', is_featured=True)
        p2 = Plan(name='🔥 Plano Casal', category='Planos Promocionais & Família', price='R$ 190,00/mês', sub='Para 2 pessoas treinando juntas', features='Válido para qualquer modalidade;Matrícula conjunta simplificada;Incentivo mútuo nos treinos', is_featured=False)
        p3 = Plan(name='Plano Família', category='Planos Promocionais & Família', price='R$ 280,00/mês', sub='Pacote especial para 3 familiares', features='Válido para 3 membros da família;Inclui Jiu-Jitsu Kids e Adulto;Maior economia por aluno', is_featured=False)
        p4 = Plan(name='Jiu-Jitsu (Seg, Qua, Sex)', category='Planos Individuais', price='R$ 100,00/mês', sub='Treinos 3x por semana', features='Treinos de fundamentos e ralas;Turmas da tarde e noite', is_featured=False)
        p5 = Plan(name='🥊 Plano MMA (Profissional & Amador)', category='Planos Individuais', price='R$ 130,00/mês', sub='MMA Profissional (Seg, Qua, Sex • 11h30) e Iniciantes (Ter, Qui • 18h00)', features='Treinos de MMA Profissional (Seg, Qua, Sex 11h30);Treinos de MMA Amador / Iniciantes (Ter, Qui 18h00);Acompanhamento do Mestre Bolivar;Preparação física e técnica completa', is_featured=False)
        db.session.add_all([p1, p2, p3, p4, p5])
        db.session.commit()

    ensure_class_groups()
    ensure_mma_classes_and_plans()
    ensure_default_accounts()




@app.cli.command('create-admin')
@click.option('--username', prompt=True)
@click.option('--name', prompt='Nome completo')
@click.option('--cpf', prompt='CPF')
@click.option('--ddd', prompt=True)
@click.option('--phone', prompt='Celular')
@click.password_option()
def create_admin(username, name, cpf, ddd, phone, password):
    """Cria o primeiro instrutor sem credenciais padrão no código."""
    if User.query.filter((User.username == username) | (User.cpf == cpf)).first():
        raise click.ClickException('Usuário ou CPF já cadastrado.')
    if len(password) < 8:
        raise click.ClickException('A senha precisa ter pelo menos 8 caracteres.')
    if not is_valid_cpf(cpf):
        raise click.ClickException('CPF inválido.')
    if not re.fullmatch(r'\d{2}', ddd) or not re.fullmatch(r'\d{9}', phone):
        raise click.ClickException('DDD ou celular inválido.')
    plan = Plan.query.order_by(Plan.id).first()
    user = User(username=username.strip(), name=name.strip(), cpf=cpf.strip(), ddd=ddd.strip(),
                phone=phone.strip(), plan=f'{plan.name} — {plan.price}', due_date='5',
                start_month=datetime.now().month, role='instrutor', payment_status='Em Dia')
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    click.echo(f'Instrutor {username} criado com sucesso.')

@app.cli.command('send-calendar-reminders')
@click.option('--minutes-ahead', default=60, type=click.IntRange(10, 240), show_default=True)
def send_calendar_reminders(minutes_ahead):
    """Envia lembretes push das turmas matriculadas; execute a cada 10 minutos."""
    now = datetime.now()
    window_start = now + timedelta(minutes=minutes_ahead - 6)
    window_end = now + timedelta(minutes=minutes_ahead + 6)
    sent, skipped, failed = 0, 0, 0
    for subscription in PushSubscription.query.filter_by(active=True).all():
        occurrences = []
        for day_date in {window_start.date(), window_end.date()}:
            for group in active_groups_for_user(subscription.user_id):
                for occurrence in class_occurrences_for_weekday(group, day_date.weekday()):
                    starts_at = datetime.combine(day_date, datetime.min.time()) + timedelta(minutes=occurrence['start'])
                    if window_start <= starts_at <= window_end:
                        occurrences.append((group, starts_at))
        if not occurrences:
            skipped += 1
            continue
        occurrence_key = '|'.join(sorted(f'{group.id}:{starts_at:%Y%m%d%H%M}' for group, starts_at in occurrences))
        if subscription.last_occurrence_key == occurrence_key:
            skipped += 1
            continue
        names = ', '.join(group.name for group, _ in occurrences)
        first_start = min(starts_at for _, starts_at in occurrences)
        try:
            deliver_push(subscription, {
                'title': 'Seu treino está chegando',
                'body': f'{names} começa às {first_start:%H:%M}.',
                'url': '/calendario', 'icon': '/static/img/favicon.png',
            })
            subscription.last_occurrence_key = occurrence_key
            db.session.commit()
            sent += 1
        except Exception as exc:
            db.session.rollback()
            failed += 1
            click.echo(f'Falha na inscrição {subscription.id}: {exc}', err=True)
    click.echo(f'Lembretes enviados: {sent}; sem lembrete novo: {skipped}; falhas: {failed}.')

@app.context_processor
def inject_user_context():
    current_user = db.session.get(User, session['user_id']) if session.get('user_id') else None
    g.user = current_user
    role = session.get('user_role', 'aluno')
    pending_attendance_count = Attendance.query.filter_by(status='pendente').count() if role in {'monitor', 'instrutor'} else 0
    pending_payments_count = User.query.filter_by(payment_status='Pendente', monthly_fee_exempt=False).count() if role in {'monitor', 'instrutor'} else 0
    contract_pending = bool(current_user and (
        current_user.membership_terms_version != MEMBERSHIP_TERMS_VERSION
        or current_user.privacy_notice_version != PRIVACY_NOTICE_VERSION
        or current_user.image_consent_scope not in {'adult', 'minor_guardian'}
    ))

    # Cálculo da contagem regressiva de 60h para o Aluno
    in_trial_period = False
    trial_hours = 0
    trial_minutes = 0
    trial_remaining_seconds = 0
    if current_user and role == 'aluno':
        created_at = current_user.created_at or datetime.utcnow()
        elapsed_seconds = (datetime.utcnow() - created_at).total_seconds()
        total_trial_seconds = 60 * 3600  # 60 horas livres
        remaining_seconds = max(0, total_trial_seconds - elapsed_seconds)
        if remaining_seconds > 0 and current_user.payment_status != 'Em Dia' and not current_user.monthly_fee_exempt:
            in_trial_period = True
            trial_remaining_seconds = max(1, int(remaining_seconds))
            trial_hours = trial_remaining_seconds // 3600
            trial_minutes = (trial_remaining_seconds % 3600) // 60

    return {
        'now': datetime.utcnow(),
        'current_user': current_user,
        'is_logged_in': 'user_id' in session,
        'user_name': session.get('user_name', ''),
        'username': session.get('username', ''),
        'user_role': role,
        'user_plan': session.get('user_plan', ''),
        'user_due_date': session.get('user_due_date', '15'),
        'user_belt_color': current_user.belt_color if current_user else 'branca',
        'user_belt_degree': current_user.belt_degree if current_user else 0,
        'pending_attendance_count': pending_attendance_count,
        'pending_payments_count': pending_payments_count,
        'contract_pending': contract_pending,
        'in_trial_period': in_trial_period,
        'trial_hours': trial_hours,
        'trial_minutes': trial_minutes,
        'trial_remaining_seconds': trial_remaining_seconds,
        'csrf_token': csrf_token,
        'locations_dict': get_locations_dict()
    }

@app.route('/')
@app.route('/index')
@app.route('/index.html')
def index():
    plans_list = Plan.query.order_by(Plan.is_featured.desc(), Plan.id.asc()).all()
    return render_template('index.html', page_title='Início', plans=plans_list)

@app.route('/turmas.html')
@app.route('/turmas')
def turmas():
    return render_template('turmas.html', page_title='Turmas')

@app.route('/calendario', methods=['GET', 'POST'])
@app.route('/calendario.html', methods=['GET', 'POST'])
@login_required
def calendario():
    ensure_class_groups()
    today = datetime.now().date()
    requested_week = request.values.get('week', '')
    try:
        anchor_date = datetime.strptime(requested_week, '%Y-%m-%d').date() if requested_week else today
    except ValueError:
        anchor_date = today
    week_start = anchor_date - timedelta(days=anchor_date.weekday())
    modality_filter = request.values.get('modality', 'todas')
    audience_filter = request.values.get('audience', 'todos')

    if request.method == 'POST':
        redirect_args = {'week': requested_week or today.isoformat(), 'modality': modality_filter,
                         'audience': audience_filter}
        if session.get('user_role') not in {'monitor', 'instrutor'}:
            flash('Somente monitores e instrutores podem adicionar aulas especiais.', 'error')
            return redirect(url_for('calendario', **redirect_args))

        title = request.form.get('title', '').strip()
        modality = request.form.get('event_modality', 'Treino especial').strip()
        notes = request.form.get('notes', '').strip()
        try:
            event_date = datetime.strptime(request.form.get('event_date', ''), '%Y-%m-%d').date()
            start = time_to_minutes(request.form.get('start_time', ''))
            end = time_to_minutes(request.form.get('end_time', ''))
        except (TypeError, ValueError):
            flash('Informe uma data e horários válidos para a aula especial.', 'error')
            return redirect(url_for('calendario', **redirect_args))

        redirect_args['week'] = event_date.isoformat()
        allowed_modalities = {'Jiu-Jitsu', 'Boxe', 'Muay Thai', 'Treino especial'}
        if not title or len(title) > 120 or modality not in allowed_modalities or len(notes) > 300:
            flash('Revise o título, a modalidade e as observações informadas.', 'error')
            return redirect(url_for('calendario', **redirect_args))
        if event_date < today:
            flash('Não é possível agendar uma nova aula em uma data passada.', 'error')
            return redirect(url_for('calendario', **redirect_args))
        if start < 6 * 60 or end > 21 * 60 + 30 or end <= start:
            flash('O horário deve estar entre 06:00 e 21:30, com o fim após o início.', 'error')
            return redirect(url_for('calendario', **redirect_args))
        if end - start < 30:
            flash('A aula especial deve durar pelo menos 30 minutos.', 'error')
            return redirect(url_for('calendario', **redirect_args))

        conflicts = []
        for class_group in ClassGroup.query.filter_by(publish_public=True).order_by(ClassGroup.id).all():
            for occurrence in class_occurrences_for_weekday(class_group, event_date.weekday()):
                if start < occurrence['end'] and end > occurrence['start']:
                    conflicts.append(f"{occurrence['name']} ({occurrence['start_time']}–{occurrence['end_time']})")
        for special in SpecialClassEvent.query.filter_by(event_date=event_date, status='agendado').all():
            special_start = time_to_minutes(special.start_time)
            special_end = time_to_minutes(special.end_time)
            if start < special_end and end > special_start:
                conflicts.append(f'{special.title} ({special.start_time}–{special.end_time})')
        if conflicts:
            flash(f"Conflito de horário com {', '.join(conflicts)}. Escolha um dos intervalos livres.", 'error')
            return redirect(url_for('calendario', **redirect_args))

        db.session.add(SpecialClassEvent(
            title=title, event_date=event_date, start_time=minutes_to_time(start),
            end_time=minutes_to_time(end), modality=modality, notes=notes or None,
            created_by_username=session.get('username', ''),
        ))
        db.session.commit()
        flash('Aula especial adicionada ao calendário com sucesso!', 'success')
        return redirect(url_for('calendario', **redirect_args))

    weekday_names = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
    displayed_events = {index: [] for index in range(7)}
    occupied_events = {index: [] for index in range(7)}

    for class_item in ClassGroup.query.filter_by(publish_public=True).order_by(ClassGroup.id).all():
        for weekday in range(7):
            occurrences = class_occurrences_for_weekday(class_item, weekday)
            occupied_events[weekday].extend(occurrences)
            if (modality_filter in {'todas', class_item.modality}
                    and audience_filter in {'todos', class_item.audience}):
                displayed_events[weekday].extend(occurrences)

    week_end = week_start + timedelta(days=6)
    special_events = SpecialClassEvent.query.filter(
        SpecialClassEvent.event_date.between(week_start, week_end),
        SpecialClassEvent.status == 'agendado',
    ).order_by(SpecialClassEvent.event_date, SpecialClassEvent.start_time).all()
    for special in special_events:
        weekday = special.event_date.weekday()
        event = {
            'start': time_to_minutes(special.start_time), 'end': time_to_minutes(special.end_time),
            'start_time': special.start_time, 'end_time': special.end_time,
            'name': special.title, 'modality': special.modality, 'audience': 'Especial',
            'instructor': special.created_by_username, 'status': special.status,
            'notes': special.notes, 'special': True,
        }
        occupied_events[weekday].append(event)
        if modality_filter in {'todas', special.modality} and audience_filter == 'todos':
            displayed_events[weekday].append(event)

    calendar_days = []
    opening, closing = 6 * 60, 21 * 60 + 30
    for weekday in range(7):
        day_date = week_start + timedelta(days=weekday)
        events = sorted(displayed_events[weekday], key=lambda item: (item['start'], item['name']))
        intervals = sorted((max(opening, item['start']), min(closing, item['end']))
                           for item in occupied_events[weekday] if item['end'] > opening and item['start'] < closing)
        merged = []
        for start, end in intervals:
            if not merged or start > merged[-1][1]:
                merged.append([start, end])
            else:
                merged[-1][1] = max(merged[-1][1], end)
        free_slots = []
        cursor = opening
        for start, end in merged:
            if start - cursor >= 30:
                free_slots.append({'start_time': minutes_to_time(cursor), 'end_time': minutes_to_time(start),
                                   'duration': start - cursor})
            cursor = max(cursor, end)
        if closing - cursor >= 30:
            free_slots.append({'start_time': minutes_to_time(cursor), 'end_time': minutes_to_time(closing),
                               'duration': closing - cursor})
        calendar_days.append({
            'label': weekday_names[weekday], 'date': day_date, 'events': events,
            'free_slots': free_slots, 'is_today': day_date == today,
        })
    current_user = db.session.get(User, session['user_id'])
    feed_token = calendar_token_serializer.dumps({'user_id': current_user.id})
    feed_path = url_for('personal_calendar_feed', token=feed_token)
    public_base_url = os.getenv('PUBLIC_BASE_URL', '').rstrip('/')
    feed_url = f'{public_base_url}{feed_path}' if public_base_url else url_for(
        'personal_calendar_feed', token=feed_token, _external=True)
    google_feed_available = feed_url.startswith('https://') and '127.0.0.1' not in feed_url and 'localhost' not in feed_url
    _, vapid_public_key, _ = push_configuration()
    return render_template(
        'calendario.html', page_title='Calendário de Aulas', calendar_days=calendar_days,
        week_start=week_start, week_end=week_end, today=today,
        previous_week=(week_start - timedelta(days=7)).isoformat(),
        next_week=(week_start + timedelta(days=7)).isoformat(), current_week=today.isoformat(),
        modality_filter=modality_filter, audience_filter=audience_filter,
        event_count=sum(len(day['events']) for day in calendar_days),
        special_event_count=len(special_events),
        default_event_date=max(today, week_start) if max(today, week_start) <= week_end else today,
        enrolled_groups=active_groups_for_user(current_user.id),
        calendar_download_url=url_for('personal_calendar_feed', token=feed_token, download='1'),
        google_calendar_url=('https://calendar.google.com/calendar/r?cid=' + urllib.parse.quote(feed_url, safe=''))
                            if google_feed_available else None,
        google_feed_available=google_feed_available,
        push_available=bool(vapid_public_key), vapid_public_key=vapid_public_key,
        push_enabled=any(item.active for item in current_user.push_subscriptions),
    )

@app.route('/calendario/minhas-turmas.ics')
def personal_calendar_feed():
    token = request.args.get('token', '')
    try:
        payload = calendar_token_serializer.loads(token)
        user = db.session.get(User, int(payload['user_id']))
    except (BadSignature, KeyError, TypeError, ValueError):
        user = None
    if not user:
        return Response('Calendário inválido.', status=404, content_type='text/plain; charset=utf-8')
    response = Response(personal_calendar_ics(user), content_type='text/calendar; charset=utf-8')
    disposition = 'attachment' if request.args.get('download') == '1' else 'inline'
    response.headers['Content-Disposition'] = f'{disposition}; filename="bj-sports-minhas-turmas.ics"'
    response.headers['Cache-Control'] = 'private, no-cache, max-age=0'
    return response

@app.route('/api/calendario/push', methods=['POST', 'DELETE'])
@login_required
def calendar_push_subscription():
    data = request.get_json(silent=True) or {}
    endpoint = str(data.get('endpoint', '')).strip()
    keys = data.get('keys') or {}
    if request.method == 'DELETE':
        subscriptions = PushSubscription.query.filter_by(user_id=session['user_id']).all()
        for item in subscriptions:
            item.active = False
        db.session.commit()
        return jsonify({'ok': True, 'enabled': False})
    if not push_configuration()[1]:
        return jsonify({'error': 'As notificações push ainda não foram configuradas no servidor.'}), 503
    if not endpoint or not keys.get('p256dh') or not keys.get('auth'):
        return jsonify({'error': 'Inscrição push inválida.'}), 400
    subscription = PushSubscription.query.filter_by(endpoint=endpoint).first()
    if subscription and subscription.user_id != session['user_id']:
        return jsonify({'error': 'Esta inscrição já pertence a outra conta.'}), 409
    if not subscription:
        subscription = PushSubscription(user_id=session['user_id'], endpoint=endpoint,
                                        p256dh=keys['p256dh'], auth=keys['auth'])
        db.session.add(subscription)
    else:
        subscription.p256dh, subscription.auth, subscription.active = keys['p256dh'], keys['auth'], True
    db.session.commit()
    return jsonify({'ok': True, 'enabled': True})

@app.route('/api/calendario/push/teste', methods=['POST'])
@login_required
def calendar_push_test():
    subscription = PushSubscription.query.filter_by(user_id=session['user_id'], active=True).order_by(
        PushSubscription.id.desc()).first()
    if not subscription:
        return jsonify({'error': 'Ative as notificações neste navegador primeiro.'}), 400
    try:
        deliver_push(subscription, {
            'title': 'BJ Sports', 'body': 'Notificações ativadas para as suas turmas.',
            'url': url_for('calendario'), 'icon': url_for('static', filename='img/favicon.png'),
        })
    except Exception as exc:
        return jsonify({'error': f'Não foi possível enviar o teste: {exc}'}), 503
    return jsonify({'ok': True})

LOCATIONS_DATA = {
    'cajazeiras-sede': {
        'id': 'cajazeiras-sede',
        'slug': 'cajazeiras-sede',
        'name': 'Cajazeiras (Sede Matriz)',
        'subtitle': 'Sede Matriz Central • Av. Estrada do Amor',
        'state': 'PB',
        'city': 'Cajazeiras',
        'address': 'Av. Estrada do Amor, s/n, Cajazeiras - PB',
        'professor_name': 'Mestre Bolivar & Equipe BJ Sports',
        'professor_title': 'Direção Técnica Matriz',
        'professor_bio': 'Sede principal e centro de formação técnica do BJ Sports.',
        'professor_phone': '5583996527997',
        'professor_phone_formatted': '(83) 99652-7997',
        'professor_instagram': '@bjsports_',
        'logo_ct': 'img/logo_original.png',
        'badge_color': 'bg-green',
        'modalities': ['Jiu-Jitsu', 'Boxe', 'Muay Thai', 'MMA', 'Preparação Física'],
        'schedules': [
            {'day': 'Segunda a Sexta', 'time': '11:30h', 'modality': 'MMA Profissional'},
            {'day': 'Segunda, Quarta e Sexta', 'time': '17:00h', 'modality': 'Jiu-Jitsu Tarde'},
            {'day': 'Segunda, Quarta e Sexta', 'time': '19:00h', 'modality': 'Jiu-Jitsu Noturno'},
            {'day': 'Terça e Quinta', 'time': '12:00h', 'modality': 'Jiu-Jitsu Meio-Dia'},
            {'day': 'Terça e Quinta', 'time': '18:00h', 'modality': 'MMA Amador'}
        ],
        'maps_link': 'https://maps.google.com/?q=Av.+Estrada+do+Amor,+Cajazeiras+-+PB',
        'description': 'Estrutura completa com octógono de treinos, tatame de competição e equipamentos de preparação física.'
    },
    'cajazeiras-tenis-clube': {
        'id': 'cajazeiras-tenis-clube',
        'slug': 'cajazeiras-tenis-clube',
        'name': 'Cajazeiras (Tênis Clube)',
        'subtitle': 'Unidade Tênis Clube • Centro',
        'state': 'PB',
        'city': 'Cajazeiras',
        'address': 'Rua Eng. Carlos Pires de Sá, Centro, Cajazeiras - PB (Tênis Clube)',
        'professor_name': 'Prof. Luiz',
        'professor_title': 'Professor Responsável • Tênis Clube',
        'professor_bio': 'Responsável pelas aulas e turmas na unidade Tênis Clube em Cajazeiras - PB.',
        'professor_phone': '5583999970203',
        'professor_phone_formatted': '(83) 99997-0203',
        'professor_photo': 'img/prof_luiz.jpg',
        'professor_instagram': '@luizricardocz',
        'logo_ct': 'img/ct_tenis_clube.png',
        'badge_color': 'bg-gold',
        'modalities': ['Jiu-Jitsu', 'Boxe', 'Muay Thai', 'MMA', 'Jiu-Jitsu Kids'],
        'schedules': [],
        'maps_link': 'https://maps.google.com/?q=Tenis+Clube+Cajazeiras+PB',
        'description': 'Estrutura no centro de Cajazeiras com tatame de alta densidade e vestiários.'
    },
    'lavras-ce': {
        'id': 'lavras-ce',
        'slug': 'lavras-ce',
        'name': 'Lavras da Mangabeira - CE',
        'subtitle': 'Unidade Lavras da Mangabeira • CE',
        'state': 'CE',
        'city': 'Lavras da Mangabeira',
        'address': 'Centro, Lavras da Mangabeira - CE',
        'professor_name': 'Prof. Washington',
        'professor_title': 'Professor Responsável • Lavras',
        'professor_bio': 'Responsável pelas aulas e turmas credenciadas BJ Sports em Lavras da Mangabeira - CE.',
        'professor_phone': '5588997371242',
        'professor_phone_formatted': '(88) 99737-1242',
        'professor_instagram': '@wins_academia',
        'logo_ct': 'img/ct_lavras.png',
        'badge_color': 'bg-blue',
        'modalities': ['Jiu-Jitsu Infantil', 'Jiu-Jitsu Adulto', 'Defesa Pessoal'],
        'schedules': [],
        'maps_link': 'https://maps.google.com/?q=Lavras+da+Mangabeira+CE',
        'description': 'Centro de Treinamento credenciado BJ Sports em Lavras da Mangabeira - CE.'
    },
    'pombal': {
        'id': 'pombal',
        'slug': 'pombal',
        'name': 'Pombal - PB',
        'subtitle': 'Unidade Pombal • Sertão PB',
        'state': 'PB',
        'city': 'Pombal',
        'address': 'Centro, Pombal - PB',
        'professor_name': 'Prof. Jorge',
        'professor_title': 'Professor Responsável • Pombal',
        'professor_bio': 'Responsável pelas aulas e turmas credenciadas BJ Sports em Pombal - PB.',
        'professor_phone': '5583991747712',
        'professor_phone_formatted': '(83) 99174-7712',
        'professor_instagram': '@bjsportspombalpb',
        'logo_ct': 'img/ct_tenis_clube.png',
        'badge_color': 'bg-gold',
        'modalities': ['Jiu-Jitsu Adulto', 'Jiu-Jitsu Infantil', 'Defesa Pessoal'],
        'schedules': [],
        'maps_link': 'https://maps.google.com/?q=Pombal+PB',
        'description': 'Centro de Treinamento credenciado BJ Sports em Pombal - PB.'
    },
    'sao-joao-do-rio-do-peixe': {
        'id': 'sao-joao-do-rio-do-peixe',
        'slug': 'sao-joao-do-rio-do-peixe',
        'name': 'São João do Rio do Peixe - PB',
        'subtitle': 'Unidade São João do Rio do Peixe • Sertão PB',
        'state': 'PB',
        'city': 'São João do Rio do Peixe',
        'address': 'Rua Padre Rolim, Centro, São João do Rio do Peixe - PB',
        'professor_name': 'Prof. Francis Hercules',
        'professor_title': 'Professor Faixa Preta Responsável',
        'professor_bio': 'Responsável pelas aulas de Jiu-Jitsu e Defesa Pessoal em São João do Rio do Peixe - PB.',
        'professor_phone': '5583999388621',
        'professor_phone_formatted': '(83) 99938-8621',
        'professor_photo': 'img/prof_francis_hercules.jpg',
        'professor_instagram': '@francishercules.bjj',
        'logo_ct': 'img/ct_francis_hercules.png',
        'badge_color': 'bg-gold',
        'modalities': ['Jiu-Jitsu Adulto', 'Jiu-Jitsu Infantil', 'Defesa Pessoal'],
        'schedules': [],
        'maps_link': 'https://maps.google.com/?q=Sao+Joao+do+Rio+do+Peixe+PB',
        'description': 'Centro de Treinamento credenciado BJ Sports em São João do Rio do Peixe - PB.'
    }
}

def slugify(text):
    if not text:
        return ''
    text = text.lower().strip()
    import re, unicodedata
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r'[^\w\s-]', '', text)
    return re.sub(r'[-\s]+', '-', text).strip('-')

def seed_locations_if_empty():
    try:
        if Location.query.count() == 0:
            for loc_id, item in LOCATIONS_DATA.items():
                loc = Location(
                    slug=item.get('slug', loc_id),
                    name=item.get('name'),
                    subtitle=item.get('subtitle'),
                    state=item.get('state', 'PB'),
                    city=item.get('city'),
                    address=item.get('address'),
                    professor_name=item.get('professor_name'),
                    professor_title=item.get('professor_title'),
                    professor_bio=item.get('professor_bio'),
                    professor_phone=item.get('professor_phone'),
                    professor_phone_formatted=item.get('professor_phone_formatted'),
                    professor_photo=item.get('professor_photo'),
                    professor_instagram=item.get('professor_instagram'),
                    logo_ct=item.get('logo_ct'),
                    badge_color=item.get('badge_color', 'bg-gold'),
                    modalities_json=json.dumps(item.get('modalities', [])),
                    maps_link=item.get('maps_link'),
                    description=item.get('description'),
                    active=True
                )
                db.session.add(loc)
            db.session.commit()
    except Exception as e:
        print(f"Error seeding locations: {e}")

def get_locations_dict():
    try:
        locs = Location.query.filter_by(active=True).all()
        if not locs:
            seed_locations_if_empty()
            locs = Location.query.filter_by(active=True).all()
        
        if not locs:
            return LOCATIONS_DATA

        result = {}
        for loc in locs:
            try:
                mods = json.loads(loc.modalities_json or '[]')
            except Exception:
                mods = []
            result[loc.slug] = {
                'id': loc.slug,
                'db_id': loc.id,
                'slug': loc.slug,
                'name': loc.name,
                'subtitle': loc.subtitle or '',
                'state': loc.state or 'PB',
                'city': loc.city or '',
                'address': loc.address or '',
                'professor_name': loc.professor_name or '',
                'professor_title': loc.professor_title or '',
                'professor_bio': loc.professor_bio or '',
                'professor_phone': loc.professor_phone or '',
                'professor_phone_formatted': loc.professor_phone_formatted or '',
                'professor_photo': loc.professor_photo or '',
                'professor_instagram': loc.professor_instagram or '',
                'logo_ct': loc.logo_ct or '',
                'badge_color': loc.badge_color or 'bg-gold',
                'modalities': mods,
                'maps_link': loc.maps_link or '',
                'description': loc.description or ''
            }
        return result
    except Exception:
        return LOCATIONS_DATA

@app.route('/locais')
@app.route('/locais/')
@app.route('/locais.html')
def lista_locais():
    return redirect(url_for('ver_local', slug='cajazeiras-sede'))

@app.route('/locais/<slug>')
@app.route('/locais/<slug>.html')
@app.route('/local/<slug>')
def ver_local(slug):
    slug_clean = slug.replace('.html', '').lower()
    locs_dict = get_locations_dict()
    location = locs_dict.get(slug_clean)
    if not location:
        location = next(iter(locs_dict.values()), LOCATIONS_DATA['cajazeiras-sede'])
    return render_template('local_detalhe.html', page_title=f"CT {location['name']} — BJ Sports", location=location)

def save_uploaded_location_image(file_storage, prefix):
    if not file_storage or not getattr(file_storage, 'filename', None):
        return None
    import os, time
    from werkzeug.utils import secure_filename
    sec_name = secure_filename(file_storage.filename)
    if not sec_name:
        return None
    ext = os.path.splitext(sec_name)[1].lower()
    if ext not in {'.png', '.jpg', '.jpeg', '.webp', '.svg', '.gif'}:
        ext = '.png'
    filename = f"{prefix}_{int(time.time())}{ext}"
    upload_dir = os.path.join(app.static_folder, 'img', 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    save_path = os.path.join(upload_dir, filename)
    file_storage.save(save_path)
    return f"img/uploads/{filename}"

@app.route('/gestao/filiais', methods=['GET', 'POST'])
@app.route('/gestao/filiais.html', methods=['GET', 'POST'])
@app.route('/gestao_filiais', methods=['GET', 'POST'])
@app.route('/locais_admin', methods=['GET', 'POST'])
@app.route('/locais_admin.html', methods=['GET', 'POST'])
def locais_admin():
    if not session.get('user_id'):
        flash('Faça login para acessar a área administrativa.', 'warning')
        return redirect(url_for('login'))
    
    current_user = db.session.get(User, session['user_id'])
    if not current_user or current_user.role not in {'instrutor', 'admin'}:
        flash('Acesso restrito à administração.', 'error')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add_location':
            name = request.form.get('name', '').strip()
            city = request.form.get('city', '').strip()
            state = request.form.get('state', 'PB').strip()
            address = request.form.get('address', '').strip()
            
            if not name or not city or not address:
                flash('Preencha os campos obrigatórios (Nome, Cidade e Endereço).', 'error')
                return redirect(url_for('locais_admin'))
                
            raw_slug = request.form.get('slug', '').strip().lower()
            if not raw_slug:
                raw_slug = slugify(f"{city}-{state}")
            else:
                raw_slug = slugify(raw_slug)

            existing = Location.query.filter_by(slug=raw_slug).first()
            if existing:
                flash(f'Já existe um local cadastrado com o identificador "{raw_slug}". Escolha outro slug.', 'error')
                return redirect(url_for('locais_admin'))

            phone_digits = ''.join(c for c in request.form.get('professor_phone', '') if c.isdigit())
            if phone_digits and not phone_digits.startswith('55'):
                phone_digits = '55' + phone_digits
            
            formatted_phone = request.form.get('professor_phone_formatted', '').strip()
            if not formatted_phone and phone_digits:
                d = phone_digits[2:] if phone_digits.startswith('55') else phone_digits
                if len(d) >= 10:
                    formatted_phone = f"({d[:2]}) {d[2:-4]}-{d[-4:]}"

            mods = [m.strip() for m in request.form.get('modalities', '').split(',') if m.strip()]
            
            prof_photo_file = request.files.get('professor_photo_file')
            prof_photo_path = save_uploaded_location_image(prof_photo_file, f"prof_{raw_slug}")

            logo_ct_file = request.files.get('logo_ct_file')
            logo_ct_path = save_uploaded_location_image(logo_ct_file, f"ct_{raw_slug}")

            new_loc = Location(
                slug=raw_slug,
                name=name,
                subtitle=request.form.get('subtitle', '').strip(),
                state=state,
                city=city,
                address=address,
                professor_name=request.form.get('professor_name', '').strip(),
                professor_title=request.form.get('professor_title', '').strip(),
                professor_bio=request.form.get('professor_bio', '').strip(),
                professor_phone=phone_digits,
                professor_phone_formatted=formatted_phone,
                professor_photo=prof_photo_path or '',
                professor_instagram=request.form.get('professor_instagram', '').strip(),
                logo_ct=logo_ct_path or 'img/logo_original.png',
                badge_color='bg-blue' if state == 'CE' else 'bg-gold',
                modalities_json=json.dumps(mods if mods else ['Jiu-Jitsu']),
                maps_link=request.form.get('maps_link', '').strip(),
                description=request.form.get('description', '').strip(),
                active=True
            )
            db.session.add(new_loc)
            db.session.commit()
            flash(f'✨ Filial "{name}" cadastrada com sucesso!', 'success')
            return redirect(url_for('locais_admin'))

        elif action == 'edit_location':
            loc_id = request.form.get('location_db_id')
            loc = db.session.get(Location, loc_id)
            if loc:
                loc.name = request.form.get('name', loc.name).strip()
                loc.subtitle = request.form.get('subtitle', loc.subtitle).strip()
                loc.city = request.form.get('city', loc.city).strip()
                loc.state = request.form.get('state', loc.state).strip()
                loc.address = request.form.get('address', loc.address).strip()
                loc.professor_name = request.form.get('professor_name', loc.professor_name).strip()
                loc.professor_title = request.form.get('professor_title', loc.professor_title).strip()
                loc.professor_bio = request.form.get('professor_bio', loc.professor_bio).strip()
                
                phone_digits = ''.join(c for c in request.form.get('professor_phone', '') if c.isdigit())
                if phone_digits and not phone_digits.startswith('55'):
                    phone_digits = '55' + phone_digits
                loc.professor_phone = phone_digits
                
                formatted_phone = request.form.get('professor_phone_formatted', '').strip()
                if not formatted_phone and phone_digits:
                    d = phone_digits[2:] if phone_digits.startswith('55') else phone_digits
                    if len(d) >= 10:
                        formatted_phone = f"({d[:2]}) {d[2:-4]}-{d[-4:]}"
                loc.professor_phone_formatted = formatted_phone

                loc.professor_instagram = request.form.get('professor_instagram', loc.professor_instagram).strip()
                mods = [m.strip() for m in request.form.get('modalities', '').split(',') if m.strip()]
                loc.modalities_json = json.dumps(mods if mods else ['Jiu-Jitsu'])
                loc.maps_link = request.form.get('maps_link', loc.maps_link).strip()
                loc.description = request.form.get('description', loc.description).strip()
                
                prof_photo_file = request.files.get('professor_photo_file')
                prof_photo_path = save_uploaded_location_image(prof_photo_file, f"prof_{loc.slug}")
                if prof_photo_path:
                    loc.professor_photo = prof_photo_path

                logo_ct_file = request.files.get('logo_ct_file')
                logo_ct_path = save_uploaded_location_image(logo_ct_file, f"ct_{loc.slug}")
                if logo_ct_path:
                    loc.logo_ct = logo_ct_path

                db.session.commit()
                flash(f'✨ Filial "{loc.name}" atualizada com sucesso!', 'success')
            return redirect(url_for('locais_admin'))

        elif action == 'delete_location':
            loc_id = request.form.get('location_db_id')
            loc = db.session.get(Location, loc_id)
            if loc:
                loc_name = loc.name
                db.session.delete(loc)
                db.session.commit()
                flash(f'🗑️ Filial "{loc_name}" removida com sucesso!', 'success')
            return redirect(url_for('locais_admin'))

    search_query = request.args.get('q', '').strip()
    state_filter = request.args.get('state', 'todos').strip()

    query = Location.query.filter_by(active=True)
    if search_query:
        query = query.filter(
            Location.name.ilike(f'%{search_query}%') |
            Location.city.ilike(f'%{search_query}%') |
            Location.professor_name.ilike(f'%{search_query}%')
        )
    if state_filter != 'todos':
        query = query.filter(Location.state == state_filter)

    locations_list = query.order_by(Location.state.asc(), Location.name.asc()).all()
    if not locations_list and not search_query and state_filter == 'todos':
        seed_locations_if_empty()
        locations_list = Location.query.filter_by(active=True).order_by(Location.state.asc(), Location.name.asc()).all()

    all_locations = Location.query.filter_by(active=True).all()
    pb_count = sum(1 for loc in all_locations if loc.state == 'PB')
    ce_count = sum(1 for loc in all_locations if loc.state == 'CE')
    professors_count = len({loc.professor_name for loc in all_locations if loc.professor_name})

    from sqlalchemy import func
    turmas_per_location = dict(
        db.session.query(ClassGroup.location_slug, func.count(ClassGroup.id))
        .filter(ClassGroup.status == 'ativa')
        .group_by(ClassGroup.location_slug)
        .all()
    )
    total_classes = sum(turmas_per_location.values())

    for loc in locations_list:
        loc.turmas_count = turmas_per_location.get(loc.slug, 0)

    overview = {
        'total': len(all_locations),
        'pb_count': pb_count,
        'ce_count': ce_count,
        'professors_count': professors_count,
        'total_classes': total_classes
    }

    return render_template(
        'locais_admin.html',
        page_title='Gestão de Filiais e Unidades',
        locations_list=locations_list,
        overview=overview,
        search_query=search_query,
        state_filter=state_filter
    )

@app.route('/blog')
@app.route('/blog.html')
def blog():
    return render_template('blog.html', page_title='Blog do Tatame')

@app.route('/api/bookings', methods=['POST'])
def create_booking():
    data = request.get_json(silent=True) or {}
    login_or_name = str(data.get('login_or_name', '')).strip()
    cpf3 = ''.join(c for c in str(data.get('cpf3', '')) if c.isdigit())
    modality = str(data.get('modality', '')).strip()
    shift_time = str(data.get('shift_time', '')).strip()
    is_experimental = bool(data.get('is_experimental'))
    class_group_id = data.get('class_group_id')
    class_time = str(data.get('class_time', '')).strip()
    try:
        class_date = datetime.strptime(str(data.get('class_date', '')), '%Y-%m-%d').date()
        class_group_id = int(class_group_id)
    except (TypeError, ValueError):
        return jsonify({'error': 'Selecione uma aula disponível.'}), 400
    if len(login_or_name) < 3 or not modality or not shift_time:
        return jsonify({'error': 'Dados obrigatórios inválidos.'}), 400
    if not is_experimental and len(cpf3) != 3:
        return jsonify({'error': 'Informe os três primeiros dígitos do CPF.'}), 400

    booking_user = None
    if session.get('user_id'):
        booking_user = db.session.get(User, session['user_id'])
    elif not is_experimental:
        candidate = User.query.filter_by(username=login_or_name).first()
        candidate_cpf = ''.join(c for c in candidate.cpf if c.isdigit()) if candidate else ''
        if not candidate or not candidate_cpf.startswith(cpf3):
            return jsonify({'error': 'Aluno não localizado. Confira o usuário e os três primeiros dígitos do CPF.'}), 404
        booking_user = candidate

    if (booking_user and booking_user.has_overdue_payments()
            and not booking_user.get_trial_status()['in_trial']):
        return jsonify({
            'error': 'Reserva bloqueada: existem mensalidades pendentes. Regularize o financeiro para agendar novas aulas.',
            'code': 'payment_required'
        }), 403

    class_group = db.session.get(ClassGroup, class_group_id)
    if (is_experimental and booking_user and class_group
            and ClassEnrollment.query.filter_by(
                user_id=booking_user.id, class_group_id=class_group.id, active=True,
            ).first()):
        return jsonify({
            'error': 'Aula experimental indisponível: você já está matriculado nesta turma.',
            'code': 'already_enrolled',
        }), 409
    occurrence = next((item for item in class_occurrences_for_weekday(class_group, class_date.weekday())
                       if item['start_time'] == class_time), None) if class_group else None
    if (not class_group or not class_group.publish_public or class_group.status not in {'ativa', 'lotada'}
            or not occurrence or class_date < datetime.now().date()):
        return jsonify({'error': 'Esta aula não está mais disponível.'}), 409
    if db.engine.dialect.name == 'postgresql':
        db.session.execute(text('SELECT id FROM class_group WHERE id = :id FOR UPDATE'), {'id': class_group.id})
    reserved = Booking.query.filter_by(
        class_group_id=class_group.id, class_date=class_date, class_time=class_time,
    ).count()
    occupied = class_group.enrolled + reserved
    if class_group.status == 'lotada' or occupied >= class_group.capacity:
        db.session.rollback()
        return jsonify({'error': 'Esta turma acabou de ficar lotada. Escolha outro horário.', 'code': 'class_full'}), 409

    booking = Booking(login_or_name=login_or_name[:120], cpf3=cpf3 or None,
                      modality=modality[:100], shift_time=shift_time[:150],
                      class_group_id=class_group.id, class_date=class_date, class_time=class_time,
                      is_experimental=is_experimental)
    db.session.add(booking)
    db.session.commit()
    remaining = max(0, class_group.capacity - occupied - 1)
    return jsonify({'id': booking.id, 'message': 'Reserva realizada com sucesso!', 'remaining': remaining}), 201

@app.route('/api/bookings/availability')
def booking_availability():
    ensure_class_groups()
    now = datetime.now()
    limit = now + timedelta(days=7)
    options = []
    classes = []
    groups = ClassGroup.query.filter(
        ClassGroup.publish_public.is_(True), ClassGroup.status.in_({'ativa', 'lotada'}),
    ).order_by(ClassGroup.modality, ClassGroup.name).all()
    for offset in range(8):
        class_date = now.date() + timedelta(days=offset)
        for class_group in groups:
            for occurrence in class_occurrences_for_weekday(class_group, class_date.weekday()):
                starts_at = datetime.combine(class_date, datetime.min.time()) + timedelta(minutes=occurrence['start'])
                if starts_at <= now or starts_at > limit:
                    continue
                reserved = Booking.query.filter_by(
                    class_group_id=class_group.id, class_date=class_date,
                    class_time=occurrence['start_time'],
                ).count()
                remaining = 0 if class_group.status == 'lotada' else max(
                    0, class_group.capacity - class_group.enrolled - reserved)
                availability = {
                    'class_group_id': class_group.id, 'class_date': class_date.isoformat(),
                    'class_time': occurrence['start_time'], 'modality': class_group.modality,
                    'name': class_group.name,
                    'label': f"{class_date.strftime('%d/%m')} — {occurrence['start_time']} ({class_group.name})",
                    'remaining': remaining,
                    'status': 'esgotado' if remaining == 0 else ('esgotando' if remaining <= 5 else 'disponivel'),
                }
                classes.append(availability)
                if remaining > 0:
                    options.append(availability)
    return jsonify({'options': options, 'classes': classes})

@app.route('/login', methods=['GET', 'POST'])
@app.route('/login.html', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'login':
            login_input = request.form.get('portalCpf', '').strip()
            password_input = request.form.get('portalPassword', '')
            clean_digits = ''.join(c for c in login_input if c.isdigit())
            
            user = User.query.filter(
                (db.func.lower(User.username) == login_input.casefold()) |
                (db.func.lower(User.name) == login_input.casefold()) |
                (User.cpf == login_input) |
                (db.func.lower(User.email) == login_input.casefold())
            ).first()

            if not user and clean_digits:
                for u in User.query.all():
                    if ''.join(c for c in u.cpf if c.isdigit()) == clean_digits:
                        user = u
                        break

            if user and user.check_password(password_input):
                session.clear()
                session['user_id'] = user.id
                session['user_name'] = user.name
                session['username'] = user.username
                session['user_role'] = user.role
                session['user_plan'] = user.plan
                session['user_due_date'] = user.due_date
                if user.must_change_password:
                    return redirect(url_for('change_temporary_password'))
                flash(f'Bem-vindo(a), {user.name}! Login realizado com sucesso.', 'success')
                next_url = request.args.get('next', '')
                if next_url and next_url.startswith('/') and not next_url.startswith('//'):
                    return redirect(next_url)
                return redirect(url_for('dashboard'))
            
            flash('Usuário, CPF, e-mail ou senha inválidos. Confira os dados informados ou solicite uma redefinição de senha ao instrutor.', 'error')
            return redirect(url_for('login'))

        elif action == 'register':
            username = request.form.get('regUsername', '').strip()
            name = request.form.get('regName', '').strip()
            cpf = request.form.get('regCpf', '').strip()
            ddd = ''.join(c for c in request.form.get('regDDD', '') if c.isdigit())
            phone = ''.join(c for c in request.form.get('regPhoneNumber', '') if c.isdigit())
            email = request.form.get('regEmail', '').strip().casefold()
            sex = request.form.get('regSex', 'prefer_not').strip()
            selected_plan = request.form.get('regPlan', '').strip()
            training_days = request.form.get('regTrainingDays', '').strip()
            combo_modalities = [value.strip() for value in request.form.getlist('comboModalities') if value.strip()]
            private_instructor_username = request.form.get('privateInstructor', '').strip()
            plan = selected_plan
            today_reg_day = str(min(datetime.now().day, 28))
            due_date = request.form.get('regDueDate', '').strip()
            if not due_date or not due_date.isdigit() or not (1 <= int(due_date) <= 28):
                due_date = today_reg_day
            password = request.form.get('regPass', '')
            accepted_membership_terms = request.form.get('acceptMembershipTerms') == 'on'
            acknowledged_privacy = request.form.get('acknowledgePrivacy') == 'on'
            accepted_legal_capacity = request.form.get('confirmLegalCapacity') == 'on'
            image_consent_scope = request.form.get('imageConsentScope', '')
            guardian_name = request.form.get('imageGuardianName', '').strip()
            guardian_cpf = request.form.get('imageGuardianCpf', '').strip()
            guardian_relationship = request.form.get('imageGuardianRelationship', '').strip()
            image_use_consent = image_consent_scope in {'adult', 'minor_guardian'}
            birth_date_raw = request.form.get('regBirthDate', '').strip()
            birth_date = None
            is_minor_by_birth_date = False

            has_medical_restriction = request.form.get('hasMedicalRestriction') == 'on'
            medical_restriction_details = request.form.get('medicalRestrictionDetails', '').strip()
            is_experimental = request.form.get('isExperimentalClass') == '1'
            medical_restriction_val = (medical_restriction_details or 'Possui restrição médica') if has_medical_restriction else None

            cpf_digits = ''.join(c for c in cpf if c.isdigit())
            errors = []
            try:
                birth_date = datetime.strptime(birth_date_raw, '%Y-%m-%d').date()
                today = datetime.now().date()
                if birth_date > today:
                    raise ValueError
                age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                is_minor_by_birth_date = age < 18
            except (TypeError, ValueError):
                errors.append('Informe uma data de nascimento válida.')
            if not re.fullmatch(r'[A-Za-z0-9_.-]{3,80}', username): errors.append('Usuário deve ter de 3 a 80 caracteres válidos.')
            if len(name) < 3: errors.append('Informe o nome completo.')
            if not is_valid_cpf(cpf_digits): errors.append('CPF inválido.')
            if not re.fullmatch(r'\d{2}', ddd) or not re.fullmatch(r'\d{9}', phone): errors.append('Telefone inválido.')
            if len(email) > 254 or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email): errors.append('Informe um e-mail válido.')
            if sex not in {'masculino', 'feminino', 'prefer_not'}: errors.append('Escolha uma opção válida para sexo.')
            if (len(password) < 8 or not re.search(r'\d', password)
                    or not re.search(r'[A-Z]', password) or not re.search(r'[a-z]', password)):
                errors.append('A senha deve ter pelo menos 8 caracteres, com número, letra maiúscula e letra minúscula.')
            if not accepted_membership_terms: errors.append('Leia e aceite o termo de adesão para concluir a matrícula.')
            if not acknowledged_privacy: errors.append('Confirme a ciência do aviso de privacidade.')
            if not accepted_legal_capacity: errors.append('Confirme que você é maior de 18 anos ou responsável legal pelo aluno.')
            if image_consent_scope not in {'adult', 'minor_guardian'}:
                errors.append('Para concluir o cadastro, autorize o uso de imagem como aluno adulto ou responsável legal pelo menor.')
            if birth_date and is_minor_by_birth_date and image_consent_scope != 'minor_guardian':
                errors.append('Aluno menor de idade exige autorização do responsável legal.')
            if image_consent_scope == 'minor_guardian':
                guardian_cpf_digits = ''.join(character for character in guardian_cpf if character.isdigit())
                if len(guardian_name) < 3: errors.append('Informe o nome completo do responsável pela autorização de imagem do menor.')
                if not is_valid_cpf(guardian_cpf_digits): errors.append('Informe um CPF válido para o responsável pela autorização de imagem.')
                if guardian_relationship not in {'mae', 'pai', 'responsavel_legal'}:
                    errors.append('Informe o vínculo do responsável legal pelo menor.')
            valid_plans = {
                f'{p.name} — {p.price}': p for p in Plan.query.all()
                if 'passe livre' not in p.name.casefold()
            }
            is_private_class = selected_plan == '__private_class__'
            private_instructor = None
            if is_private_class:
                private_instructor = User.query.filter_by(username=private_instructor_username).first()
                if not private_instructor or private_instructor.role not in {'professor', 'instrutor', 'monitor'}:
                    errors.append('Escolha um professor ou monitor válido para a aula particular.')
            elif selected_plan not in valid_plans:
                errors.append('Modalidade inválida.')
            selected_plan_record = valid_plans.get(selected_plan)
            expected_combo_count = selected_plan_record.get_selection_count() if selected_plan_record else 0
            allowed_combo_modalities = {'Jiu-Jitsu', 'Boxe', 'Muay Thai', 'MMA'}
            if expected_combo_count:
                if len(combo_modalities) != expected_combo_count or len(set(combo_modalities)) != expected_combo_count:
                    errors.append(f'Escolha {expected_combo_count} modalidades diferentes para este combo.')
                elif any(modality not in allowed_combo_modalities for modality in combo_modalities):
                    errors.append('Uma das modalidades escolhidas para o combo é inválida.')
            if selected_plan_record and selected_plan_record.requires_all_days():
                training_days = 'todos'
            training_day_labels = {'ter-qui': 'Ter, Qui', 'seg-qua-sex': 'Seg, Qua, Sex', 'todos': 'Todos os dias'}
            if training_days not in training_day_labels:
                errors.append('Escolha os dias de treino.')
            elif is_private_class and private_instructor:
                plan = f'Aula Particular com {private_instructor.name} • {training_day_labels[training_days]}'
            elif selected_plan_record:
                plan_name = selected_plan_record.name
                plan_price = selected_plan_record.get_price_for_schedule(training_days)
                plan_name = re.sub(r'\s*\((?:Seg,\s*Qua,\s*Sex|Ter,\s*Qui)\)\s*$', '', plan_name)
                plan = f'{plan_name} • {training_day_labels[training_days]} — {plan_price}'
            if errors:
                for error in errors: flash(error, 'error')
                return redirect(url_for('login', mode='register'))

            existing_user = User.query.filter(
                (User.username == username) | (User.cpf == cpf) | (db.func.lower(User.email) == email)
            ).first()
            if not existing_user:
                new_user = User(
                    username=username,
                    name=name,
                    cpf=cpf,
                    ddd=ddd,
                    phone=phone,
                    email=email,
                    sex=sex,
                    plan=plan,
                    due_date=due_date,
                    start_month=datetime.now().month,
                    role='aluno',
                    payment_status='Pendente',
                    membership_terms_version=MEMBERSHIP_TERMS_VERSION,
                    membership_terms_accepted_at=datetime.utcnow(),
                    privacy_notice_version=PRIVACY_NOTICE_VERSION,
                    privacy_notice_accepted_at=datetime.utcnow(),
                    image_use_consent=image_use_consent,
                    image_use_consent_at=datetime.utcnow(),
                    image_consent_scope=image_consent_scope,
                    image_consent_guardian_name=guardian_name if image_consent_scope == 'minor_guardian' else None,
                    image_consent_guardian_cpf=guardian_cpf if image_consent_scope == 'minor_guardian' else None,
                    image_consent_guardian_relationship=guardian_relationship if image_consent_scope == 'minor_guardian' else None,
                    medical_restriction=medical_restriction_val,
                    is_experimental=is_experimental,
                    birth_date=birth_date,
                    selected_modalities=', '.join(
                        combo_modalities if expected_combo_count else (
                            selected_plan_record.get_modalities() if selected_plan_record else []
                        )
                    ) or None,
                )
                new_user.set_password(password)
                db.session.add(new_user)
                db.session.flush()
                db.session.add(ContractAcceptance(
                    user_id=new_user.id,
                    membership_terms_version=MEMBERSHIP_TERMS_VERSION,
                    privacy_notice_version=PRIVACY_NOTICE_VERSION,
                    image_consent_scope=image_consent_scope,
                    source='registration',
                ))
                db.session.commit()
                session['user_id'] = new_user.id
                session['user_name'] = new_user.name
                session['username'] = new_user.username
                session['user_role'] = new_user.role
                session['user_plan'] = new_user.plan
                session['user_due_date'] = new_user.due_date
                session['first_registration'] = True
            else:
                flash('Usuário, CPF ou e-mail já cadastrado. Entre com sua senha.', 'error')
                return redirect(url_for('login', mode='register'))
            return redirect(url_for('dashboard'))

        elif action == 'update_due_date':
            new_due_date = request.form.get('due_date', '5')
            user_id = session.get('user_id')
            if user_id and new_due_date in {'5', '15', '25'}:
                user = db.session.get(User, user_id)
                if user:
                    result = change_user_due_date_with_proration(user, new_due_date)
                    db.session.commit()
                    session['user_due_date'] = new_due_date
                    flash(f'Dia de vencimento alterado para Dia {new_due_date}. Adicional proporcional: {result["days"]} dia(s), R$ {result["amount"]:.2f}.', 'success')
            return redirect(url_for('mensalidades_aluno'))

    if request.args.get('logout') == '1' or request.args.get('switch') == '1':
        session.clear()

    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    available_plans = Plan.query.order_by(Plan.category, Plan.id).all()
    registration_modalities, registration_combos = [], []
    for available_plan in available_plans:
        if 'passe livre' in available_plan.name.casefold():
            continue
        option = {
            'value': f'{available_plan.name} — {available_plan.price}', 'label': available_plan.name,
            'prices': {
                'ter-qui': available_plan.get_price_for_schedule('ter-qui'),
                'seg-qua-sex': available_plan.get_price_for_schedule('seg-qua-sex'),
                'todos': available_plan.get_price_for_schedule('todos'),
            },
            'modalities': available_plan.get_modalities(),
            'selection_count': available_plan.get_selection_count(),
            'shared_type': available_plan.get_shared_type(),
            'force_all_days': available_plan.requires_all_days(),
            'discount_percent': float(available_plan.discount_percent or 0),
            'description': available_plan.sub or '',
            'features': [item.strip() for item in (available_plan.features or '').split(';') if item.strip()],
        }
        if available_plan.category == 'Planos Individuais':
            modalities = available_plan.get_modalities()
            if len(modalities) == 1 and modalities[0] in {'Jiu-Jitsu', 'Boxe', 'Muay Thai', 'MMA'}:
                option['label'] = modalities[0]
                registration_modalities.append(option)
        else:
            registration_combos.append(option)

    registration_combos.append({'value': '__private_class__', 'label': 'Aula Particular'})
    professionals = User.query.filter(User.role.in_({'professor', 'instrutor', 'monitor'})).all()
    professional_groups = {'professores': [], 'monitores': []}
    seen_professional_names = set()
    for professional in sorted(professionals, key=lambda user: (0 if user.role in {'professor', 'instrutor'} else 1, user.name.casefold())):
        normalized_name = professional.name.strip().casefold()
        if normalized_name in seen_professional_names:
            continue
        seen_professional_names.add(normalized_name)
        group = 'professores' if professional.role in {'professor', 'instrutor'} else 'monitores'
        professional_groups[group].append({'username': professional.username, 'name': professional.name})

    return render_template('login.html', page_title='Área de Membros', is_logged_in=False,
                           available_plans=available_plans,
                           registration_modalities=registration_modalities,
                           registration_combos=registration_combos,
                           professional_groups=professional_groups,
                           membership_terms_version=MEMBERSHIP_TERMS_VERSION,
                           privacy_notice_version=PRIVACY_NOTICE_VERSION)

@app.route('/dashboard.html')
@app.route('/dashboard')
@login_required
def dashboard():
    user = db.session.get(User, session['user_id'])
    today = datetime.now()
    attendance_total = Attendance.query.filter_by(user_id=user.id, status='confirmado').count()
    attendance_month = Attendance.query.filter(
        Attendance.user_id == user.id,
        Attendance.status == 'confirmado',
        db.extract('year', Attendance.training_date) == today.year,
        db.extract('month', Attendance.training_date) == today.month
    ).count()
    checkin_requests = Booking.query.filter_by(login_or_name=user.username).count()
    overdue = user.get_overdue_details()
    plan_parts = user.plan.split('—', 1)
    plan_name = plan_parts[0].strip()
    plan_price = plan_parts[1].strip() if len(plan_parts) > 1 else ''
    cpf_digits = ''.join(character for character in user.cpf if character.isdigit())
    masked_cpf = f'***.***.***-{cpf_digits[-2:]}' if len(cpf_digits) >= 2 else 'Não informado'
    enrollment_duration = format_enrollment_duration(user.created_at, today)
    return render_template('dashboard.html', page_title='Bem-vindo', profile_user=user,
                           first_name=user.name.split()[0], plan_name=plan_name,
                           plan_price=plan_price, attendance_total=attendance_total,
                           attendance_month=attendance_month, checkin_requests=checkin_requests,
                           overdue=overdue, masked_cpf=masked_cpf,
                           enrollment_duration=enrollment_duration,
                           is_first_reg=session.pop('first_registration', False))

@app.route('/presencas', methods=['GET', 'POST'])
@app.route('/presencas.html', methods=['GET', 'POST'])
@login_required
def presencas():
    ensure_class_groups()
    user = db.session.get(User, session['user_id'])
    user_active_enrollments = [enrollment for enrollment in user.class_enrollments if enrollment.active]
    trial_status = user.get_trial_status()
    has_overdue = user.has_overdue_payments() and not trial_status['in_trial']
    if request.method == 'POST':
        action = request.form.get('action', 'request_checkin')
        if action in {'confirm_attendance', 'reject_attendance'}:
            if session.get('user_role') not in {'monitor', 'instrutor'}:
                flash('Somente monitores e instrutores podem analisar presenças.', 'error')
                return redirect(url_for('presencas'))
            attendance = db.session.get(Attendance, request.form.get('attendance_id', type=int))
            if not attendance or attendance.status != 'pendente':
                flash('Solicitação de presença não encontrada ou já processada.', 'warning')
                return redirect(url_for('presencas'))
            attendance.status = 'confirmado' if action == 'confirm_attendance' else 'negado'
            attendance.confirmed_by_username = user.username
            attendance.confirmed_at = datetime.utcnow()
            db.session.commit()
            if attendance.status == 'confirmado':
                flash(f'Presença de {attendance.user.name} confirmada!', 'success')
            else:
                flash(f'Presença de {attendance.user.name} negada.', 'info')
            return redirect(url_for('presencas'))
        if has_overdue:
            flash('Check-in bloqueado: existem mensalidades pendentes. Regularize o financeiro para registrar novas aulas.', 'error')
            return redirect(url_for('presencas'))

        # VALIDAÇÃO DE TURMA E DIA AUTORIZADO DO ALUNO
        today_date = datetime.now().date()
        today_weekday = today_date.weekday()
        weekday_names = {0: 'Segunda-feira', 1: 'Terça-feira', 2: 'Quarta-feira', 3: 'Quinta-feira', 4: 'Sexta-feira', 5: 'Sábado', 6: 'Domingo'}
        today_name = weekday_names.get(today_weekday, '')

        target_class_id = request.form.get('class_group_id', type=int)
        target_class = db.session.get(ClassGroup, target_class_id) if target_class_id else None
        is_experimental = request.form.get('is_experimental') == '1'

        enrolled_class_ids = {enrollment.class_group_id for enrollment in user_active_enrollments}
        if is_experimental and user_active_enrollments and (
                target_class is None or target_class.id in enrolled_class_ids):
            flash('Aula experimental indisponível: você já está matriculado nesta turma.', 'error')
            return redirect(url_for('presencas'))

        allowed_weekdays = set()

        if user_active_enrollments:
            for enr in user_active_enrollments:
                cg = enr.class_group
                for sch in (cg.schedules or []):
                    sch_lower = sch.lower()
                    if 'seg' in sch_lower: allowed_weekdays.add(0)
                    if 'ter' in sch_lower: allowed_weekdays.add(1)
                    if 'qua' in sch_lower: allowed_weekdays.add(2)
                    if 'qui' in sch_lower: allowed_weekdays.add(3)
                    if 'sex' in sch_lower: allowed_weekdays.add(4)
                    if 'sáb' in sch_lower or 'sab' in sch_lower: allowed_weekdays.add(5)
                    if 'dom' in sch_lower: allowed_weekdays.add(6)

        if not allowed_weekdays:
            normalized_plan = (user.plan or '').lower()
            if 'passe livre' in normalized_plan or 'combo' in normalized_plan or 'todos os dias' in normalized_plan:
                allowed_weekdays = {0, 1, 2, 3, 4, 5, 6}
            elif all(d in normalized_plan for d in ('seg', 'qua', 'sex')):
                allowed_weekdays = {0, 2, 4}
            elif all(d in normalized_plan for d in ('ter', 'qui')):
                allowed_weekdays = {1, 3}
            else:
                allowed_weekdays = {0, 1, 2, 3, 4, 5}

        # 1. Bloqueia se hoje não for um dia de treino autorizado para o aluno
        if today_weekday not in allowed_weekdays:
            flash(f'⚠️ Check-in não permitido: você não possui treino agendado para hoje ({today_name}) no seu plano/turma ({user.plan}).', 'error')
            return redirect(url_for('presencas'))

        # 2. Bloqueia se o aluno tentar fazer check-in numa turma onde não está inscrito
        if target_class and user_active_enrollments:
            if target_class.id not in enrolled_class_ids:
                flash(f'⚠️ Check-in não permitido: você não está cadastrado na turma "{target_class.name}". Você só pode fazer check-in nas turmas em que está matriculado.', 'error')
                return redirect(url_for('presencas'))

        existing = Attendance.query.filter_by(user_id=session['user_id'], training_date=today_date).first()
        if existing:
            if existing.status == 'confirmado':
                message = 'Sua presença de hoje já foi confirmada.'
            elif existing.status == 'negado':
                message = 'Seu check-in de hoje não foi confirmado pelo instrutor.'
            else:
                message = 'Seu check-in de hoje já está aguardando confirmação do instrutor.'
            flash(message, 'info')
        else:
            active_enrollment = target_class or next((item.class_group for item in user_active_enrollments), None)
            db.session.add(Attendance(
                user_id=session['user_id'], status='pendente',
                modality=active_enrollment.modality if active_enrollment else get_attendance_modality(user.plan),
                class_group_id=active_enrollment.id if active_enrollment else None,
            ))
            db.session.commit()
            flash('Check-in enviado! Aguarde a confirmação do instrutor.', 'success')
        return redirect(url_for('presencas'))
    today = datetime.now().date()
    confirmed_query = Attendance.query.filter_by(user_id=user.id, status='confirmado')
    first_confirmed = confirmed_query.order_by(Attendance.training_date.asc()).first()
    attendance_windows = {
        days: Attendance.query.filter(
            Attendance.user_id == user.id,
            Attendance.status == 'confirmado',
            Attendance.training_date >= today - timedelta(days=days - 1),
            Attendance.training_date <= today
        ).count()
        for days in (30, 90, 180)
    }
    normalized_plan = user.plan.lower()
    if all(day in normalized_plan for day in ('seg', 'qua', 'sex')):
        training_weekdays = {0, 2, 4}
    elif all(day in normalized_plan for day in ('ter', 'qui')):
        training_weekdays = {1, 3}
    elif 'passe livre' in normalized_plan or 'todos os dias' in normalized_plan:
        training_weekdays = {0, 1, 2, 3, 4}
    else:
        training_weekdays = set()
    attendance_expected = {
        days: sum(
            1 for offset in range(days)
            if (today - timedelta(days=offset)).weekday() in training_weekdays
        ) if training_weekdays else None
        for days in (30, 90, 180)
    }
    attendance_percentages = {
        days: min(100, round(attendance_windows[days] / attendance_expected[days] * 100))
        if attendance_expected[days] else None
        for days in (30, 90, 180)
    }
    attendance_metric_available = {
        days: bool(first_confirmed and first_confirmed.training_date <= today - timedelta(days=max(1, days - 4)))
        for days in (30, 90, 180)
    }
    recent_attendances = Attendance.query.filter_by(user_id=user.id).order_by(
        Attendance.training_date.desc(), Attendance.created_at.desc()
    ).limit(12).all()
    today_attendance = Attendance.query.filter_by(user_id=user.id, training_date=today).first()
    pending_confirmations = []
    pending_confirmation_groups = []
    if session.get('user_role') in {'monitor', 'instrutor'}:
        pending_confirmations = Attendance.query.filter_by(status='pendente').order_by(
            Attendance.training_date.desc(), Attendance.modality.asc(), Attendance.created_at.asc()
        ).all()
        group_map = {}
        for attendance in pending_confirmations:
            key = (attendance.training_date, attendance.modality)
            if key not in group_map:
                group = {'date': attendance.training_date, 'modality': attendance.modality, 'items': []}
                group_map[key] = group
                pending_confirmation_groups.append(group)
            group_map[key]['items'].append(attendance)
    return render_template('presencas.html', page_title='Presenças & Treinos',
                           has_overdue=has_overdue,
                           attendance_windows=attendance_windows,
                           attendance_expected=attendance_expected,
                           attendance_percentages=attendance_percentages,
                           attendance_metric_available=attendance_metric_available,
                           recent_attendances=recent_attendances,
                           has_active_enrollment=bool(user_active_enrollments),
                           today_attendance=today_attendance,
                           pending_confirmations=pending_confirmations,
                           pending_confirmation_groups=pending_confirmation_groups)

@app.route('/mensalidades_aluno', methods=['GET', 'POST'])
@app.route('/mensalidades_aluno.html', methods=['GET', 'POST'])
@login_required
def mensalidades_aluno():
    if request.method == 'POST':
        new_due_date = request.form.get('due_date', '15')
        if new_due_date in {'5', '15', '25'}:
            user = db.session.get(User, session['user_id'])
            result = change_user_due_date_with_proration(user, new_due_date)
            db.session.commit()
            session['user_due_date'] = new_due_date
            flash(f'Data de vencimento atualizada para o Dia {new_due_date}. Foram adicionados {result["days"]} dia(s) proporcionais (R$ {result["amount"]:.2f}) à sua fatura.', 'success')
        return redirect(url_for('mensalidades_aluno'))
    user = db.session.get(User, session['user_id'])
    overdue = user.get_overdue_details()
    now = datetime.now()
    open_payment = MonthlyPayment.query.filter(
        MonthlyPayment.user_id == user.id,
        MonthlyPayment.status != 'pago',
        (MonthlyPayment.year * 100 + MonthlyPayment.month) >= (now.year * 100 + now.month),
    ).order_by(MonthlyPayment.year.asc(), MonthlyPayment.month.asc()).first()
    return render_template('mensalidades_aluno.html', page_title='Minhas Mensalidades',
                           finance_user=user, overdue=overdue,
                           open_payment=open_payment,
                           has_overdue=overdue['count'] > 0)

@app.route('/financeiro_dashboard')
@app.route('/financeiro_dashboard.html')
@role_required('instrutor')
def financeiro_dashboard():
    today = datetime.now()
    selected_year = request.args.get('year', type=int) or today.year
    selected_month = request.args.get('month', type=int) or today.month
    selected_month = selected_month if 1 <= selected_month <= 12 else today.month
    due_filter = request.args.get('due', 'todos')
    status_filter = request.args.get('status', 'todos')

    query = User.query
    if due_filter in {'5', '15', '25'}:
        query = query.filter(User.due_date == due_filter)
    if status_filter == 'em_dia':
        query = query.filter(User.payment_status == 'Em Dia', User.monthly_fee_exempt.is_(False))
    elif status_filter == 'pendente':
        query = query.filter(User.payment_status == 'Pendente', User.monthly_fee_exempt.is_(False))
    elif status_filter == 'isento':
        query = query.filter(User.monthly_fee_exempt.is_(True))
    users = query.order_by(User.name.asc()).all()

    monthly = []
    for month in range(1, 13):
        expected = received = overdue = 0.0
        for user in users:
            if selected_year == today.year and user.start_month and month < user.start_month:
                continue
            schedule = {int(item['month']): item['status'] for item in user.get_month_schedule(month, selected_year)}
            payment_status = schedule.get(month, 'futuro')
            payment = next((item for item in user.payments if item.year == selected_year and item.month == month), None)
            amount = float(payment.amount) if payment else user.get_numeric_price(selected_year, month)
            expected += amount
            if payment_status == 'pago':
                received += amount
            elif payment_status == 'atrasado':
                overdue += amount
        monthly.append({'month': month, 'expected': expected, 'received': received, 'overdue': overdue})

    current = monthly[selected_month - 1]
    expected_total = current['expected']
    received_total = current['received']
    overdue_total = current['overdue']
    receipt_rate = round((received_total / expected_total * 100), 1) if expected_total else 0

    debtors = []
    for user in users:
        details = user.get_overdue_details(selected_month)
        if details['count']:
            debtors.append({'name': user.name, 'plan': user.plan.split('—')[0].strip(),
                            'months': details['count'], 'total': details['total_debt'],
                            'due_date': user.due_date})
    debtors.sort(key=lambda item: item['total'], reverse=True)

    due_distribution = [
        {'day': day, 'count': sum(1 for user in users if user.due_date == day)}
        for day in ('5', '15', '25')
    ]
    max_month_value = max((item['expected'] for item in monthly), default=1) or 1
    years = list(range(min(selected_year, today.year) - 2, today.year + 1))

    return render_template('financeiro_dashboard.html', page_title='Dashboard Financeiro',
                           selected_year=selected_year, selected_month=selected_month,
                           due_filter=due_filter, status_filter=status_filter, years=years,
                           expected_total=expected_total, received_total=received_total,
                           overdue_total=overdue_total, receipt_rate=receipt_rate,
                           monthly=monthly, max_month_value=max_month_value,
                           debtors=debtors[:6], due_distribution=due_distribution,
                           filtered_users=len(users))

@app.route('/cards_planos', methods=['GET', 'POST'])
@app.route('/cards_planos.html', methods=['GET', 'POST'])
@login_required
def cards_planos():
    if request.method == 'POST':
        if g.user and g.user.role == 'instrutor':
            action = request.form.get('action')
            if action == 'create':
                name = request.form.get('name', '').strip()
                category = request.form.get('category', '').strip()
                price = request.form.get('price', '').strip()
                sub = request.form.get('sub', '').strip()
                features = request.form.get('features', '').strip()
                is_featured = 'is_featured' in request.form
                new_plan = Plan(name=name, category=category, price=price, sub=sub, features=features, is_featured=is_featured)
                db.session.add(new_plan)
                db.session.commit()
                flash(f'Plano "{name}" cadastrado com sucesso!', 'success')
            elif action == 'update':
                plan_id = request.form.get('plan_id')
                plan = db.session.get(Plan, plan_id)
                if plan:
                    plan.name = request.form.get('name', '').strip()
                    plan.category = request.form.get('category', '').strip()
                    plan.price = request.form.get('price', '').strip()
                    plan.sub = request.form.get('sub', '').strip()
                    plan.features = request.form.get('features', '').strip()
                    plan.is_featured = 'is_featured' in request.form
                    db.session.commit()
                    flash(f'Plano #{plan.id} ("{plan.name}") atualizado com sucesso!', 'success')
            elif action == 'delete':
                plan_id = request.form.get('plan_id')
                plan = db.session.get(Plan, plan_id)
                if plan:
                    db.session.delete(plan)
                    db.session.commit()
                    flash(f'Plano #{plan.id} removido do catálogo.', 'info')
        return redirect(url_for('cards_planos'))

    all_plans = Plan.query.order_by(Plan.id.asc()).all()
    user_counts = {}
    all_users = User.query.all()
    for u in all_users:
        if u.plan:
            for p in all_plans:
                if p.name.lower() in u.plan.lower():
                    user_counts[p.id] = user_counts.get(p.id, 0) + 1
                    break

    plan_cards_data = []
    total_revenue_estimated = 0.0
    total_students_enrolled = 0

    for plan in all_plans:
        subscribers = user_counts.get(plan.id, 0)
        numbers = re.findall(r'\d+(?:[.,]\d+)?', plan.price)
        unit_price = 0.0
        if numbers:
            try:
                unit_price = float(numbers[0].replace('.', '').replace(',', '.'))
            except ValueError:
                unit_price = 0.0
        estimated_revenue = subscribers * unit_price
        total_revenue_estimated += estimated_revenue
        total_students_enrolled += subscribers

        feature_list = [f.strip() for f in plan.features.split(';') if f.strip()] if plan.features else []

        plan_cards_data.append({
            'plan': plan,
            'subscribers': subscribers,
            'estimated_revenue': f"R$ {estimated_revenue:,.2f}".replace('.', 'X').replace(',', '.').replace('X', ','),
            'features_list': feature_list,
            'unit_price': unit_price,
            'modalities': plan.get_modalities()
        })

    return render_template(
        'cards_planos.html',
        page_title='Cards Planos • Financeiro',
        plan_cards=plan_cards_data,
        total_plans=len(all_plans),
        total_subscribers=total_students_enrolled,
        total_revenue=f"R$ {total_revenue_estimated:,.2f}".replace('.', 'X').replace(',', '.').replace('X', ',')
    )

@app.route('/planos_admin', methods=['GET', 'POST'])
@app.route('/planos_admin.html', methods=['GET', 'POST'])
@role_required('instrutor')
def planos_admin():
    allowed_categories = {'Planos Individuais', 'Combos & Planos Especiais'}
    allowed_modalities = {'Jiu-Jitsu', 'Boxe', 'Muay Thai', 'MMA'}
    return_tab = request.form.get('return_tab', request.args.get('tab', 'modalities'))
    if return_tab not in {'modalities', 'plans'}:
        return_tab = 'modalities'

    def admin_redirect():
        return redirect(url_for('planos_admin', tab=return_tab))

    def plan_form_values():
        name = request.form.get('name', '').strip()
        category = request.form.get('category', '').strip()
        schedule_prices = {
            'ter-qui': request.form.get('price_ter_qui', request.form.get('price', '')).strip(),
            'seg-qua-sex': request.form.get('price_seg_qua_sex', request.form.get('price', '')).strip(),
            'todos': request.form.get('price_all_days', request.form.get('price', '')).strip(),
        }
        price = schedule_prices['todos']
        sub = request.form.get('sub', '').strip()
        features = ';'.join(
            item.strip() for item in request.form.get('features', '').split(';') if item.strip()
        )
        modalities = list(dict.fromkeys(
            item for item in request.form.getlist('modalities') if item in allowed_modalities
        ))
        errors = []
        discount_raw = request.form.get('discount_percent', '0').strip().replace(',', '.')
        try:
            discount_percent = float(discount_raw)
            if not 0 <= discount_percent <= 100:
                raise ValueError
        except ValueError:
            discount_percent = 0
            errors.append('Informe um desconto entre 0% e 100%.')
        selection_count = request.form.get('selection_count', type=int)
        selection_count = 0 if selection_count is None else selection_count
        shared_type = request.form.get('shared_type', 'none').strip()
        force_all_days = request.form.get('force_all_days') == '1'
        if selection_count not in range(0, 5):
            errors.append('A quantidade de modalidades deve estar entre 0 e 4.')
        if shared_type not in {'none', 'couple', 'family'}:
            errors.append('Selecione um tipo de compartilhamento válido.')
        if selection_count > len(modalities):
            errors.append('A quantidade escolhida pelo aluno não pode exceder as modalidades incluídas.')
        if len(name) < 3 or len(name) > 120:
            errors.append('Informe um nome de plano com 3 a 120 caracteres.')
        if category not in allowed_categories:
            errors.append('Selecione uma categoria válida.')
        if shared_type in {'couple', 'family'}:
            schedule_prices['ter-qui'] = 'Calculado via Desconto'
            schedule_prices['seg-qua-sex'] = 'Calculado via Desconto'
            schedule_prices['todos'] = 'Calculado via Desconto'
            price = 'Calculado via Desconto'
        else:
            for label, schedule_price in (
                ('Ter - Qui', schedule_prices['ter-qui']),
                ('Seg - Qua - Sex', schedule_prices['seg-qua-sex']),
                ('Todos os dias', schedule_prices['todos']),
            ):
                if not re.fullmatch(r'R\$\s*\d{1,3}(?:\.\d{3})*,\d{2}(?:/mês)?', schedule_price):
                    errors.append(f'Informe o valor de {label} no formato R$ 120,00/mês.')
        if category == 'Planos Individuais' and len(modalities) != 1:
            errors.append('Plano individual deve possuir exatamente uma modalidade.')
        if category == 'Combos & Planos Especiais' and not modalities:
            errors.append('Selecione ao menos uma modalidade para o combo ou plano especial.')
        return (name, category, price, sub, features, modalities, schedule_prices,
                discount_percent, selection_count, shared_type, force_all_days, errors)

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'create':
            (name, category, price, sub, features, modalities, schedule_prices,
             discount_percent, selection_count, shared_type, force_all_days, errors) = plan_form_values()
            if Plan.query.filter(db.func.lower(Plan.name) == name.casefold()).first():
                errors.append('Já existe um plano com esse nome.')
            if errors:
                for error in errors:
                    flash(error, 'error')
                return admin_redirect()
            is_featured = 'is_featured' in request.form
            new_plan = Plan(
                name=name, category=category, price=price, sub=sub or None,
                features=features or None, modality=', '.join(modalities), is_featured=is_featured,
                price_ter_qui=schedule_prices['ter-qui'],
                price_seg_qua_sex=schedule_prices['seg-qua-sex'],
                price_all_days=schedule_prices['todos'],
                discount_percent=discount_percent,
                selection_count=selection_count, shared_type=shared_type,
                force_all_days=force_all_days,
            )
            db.session.add(new_plan)
            db.session.commit()
            flash(f'Plano e modalidades de “{name}” cadastrados. O catálogo já foi atualizado.', 'success')
        elif action == 'update':
            plan_id = request.form.get('plan_id', type=int)
            plan = db.session.get(Plan, plan_id)
            if plan:
                (name, category, price, sub, features, modalities, schedule_prices,
                 discount_percent, selection_count, shared_type, force_all_days, errors) = plan_form_values()
                duplicate = Plan.query.filter(db.func.lower(Plan.name) == name.casefold(), Plan.id != plan.id).first()
                if duplicate:
                    errors.append('Já existe outro plano com esse nome.')
                if errors:
                    for error in errors:
                        flash(error, 'error')
                    return admin_redirect()
                old_name, old_price = plan.name, plan.price
                old_schedule_prices = {
                    key: plan.get_price_for_schedule(key)
                    for key in ('ter-qui', 'seg-qua-sex', 'todos')
                }
                plan.name, plan.category, plan.price = name, category, price
                plan.sub, plan.features = sub or None, features or None
                plan.modality = ', '.join(modalities)
                plan.price_ter_qui = schedule_prices['ter-qui']
                plan.price_seg_qua_sex = schedule_prices['seg-qua-sex']
                plan.price_all_days = schedule_prices['todos']
                plan.discount_percent = discount_percent
                plan.selection_count = selection_count
                plan.shared_type = shared_type
                plan.force_all_days = force_all_days
                plan.is_featured = 'is_featured' in request.form
                synchronized = 0
                for user in User.query.filter(User.plan.ilike(f'{old_name}%')).all():
                    updated_plan = re.sub(rf'^{re.escape(old_name)}', name, user.plan, count=1)
                    plan_lower = updated_plan.casefold()
                    schedule_key = 'ter-qui' if 'ter, qui' in plan_lower or 'ter & qui' in plan_lower else (
                        'todos' if 'todos os dias' in plan_lower else 'seg-qua-sex'
                    )
                    previous_price = old_schedule_prices[schedule_key]
                    current_price = schedule_prices[schedule_key]
                    if previous_price in updated_plan:
                        updated_plan = updated_plan.replace(previous_price, current_price, 1)
                    elif old_price in updated_plan:
                        updated_plan = updated_plan.replace(old_price, current_price, 1)
                    user.plan = updated_plan
                    synchronized += 1
                db.session.commit()
                flash(f'“{plan.name}” atualizado em todo o sistema e em {synchronized} matrícula(s).', 'success')
        elif action == 'delete':
            plan_id = request.form.get('plan_id', type=int)
            plan = db.session.get(Plan, plan_id)
            if plan:
                linked_users = User.query.filter(User.plan.ilike(f'{plan.name}%')).count()
                if linked_users:
                    flash(f'Não é possível excluir: {linked_users} aluno(s) utilizam este plano.', 'error')
                    return admin_redirect()
                db.session.delete(plan)
                db.session.commit()
                flash(f'Plano “{plan.name}” removido do catálogo.', 'info')
        return admin_redirect()

    plans_list = Plan.query.order_by(Plan.category, Plan.name).all()
    usage = {plan.id: User.query.filter(User.plan.ilike(f'{plan.name}%')).count() for plan in plans_list}
    active_class_groups = ClassGroup.query.filter_by(status='ativa').order_by(ClassGroup.name).all()
    schedules_by_modality = {}
    for class_group in active_class_groups:
        schedules_by_modality.setdefault(class_group.modality, [])
        for schedule in class_group.schedules:
            if schedule not in schedules_by_modality[class_group.modality]:
                schedules_by_modality[class_group.modality].append(schedule)
    plan_schedules = {}
    for plan in plans_list:
        plan_schedules[plan.id] = []
        for modality in plan.get_modalities():
            for schedule in schedules_by_modality.get(modality, []):
                if schedule not in plan_schedules[plan.id]:
                    plan_schedules[plan.id].append(schedule)
    return render_template(
        'planos_admin.html', page_title='Planos e Modalidades', plans=plans_list,
        plan_usage=usage, allowed_modalities=sorted(allowed_modalities),
        individual_count=sum(1 for plan in plans_list if plan.category == 'Planos Individuais'),
        special_count=sum(1 for plan in plans_list if plan.category != 'Planos Individuais'),
        active_tab=return_tab, plan_schedules=plan_schedules,
    )

@app.route('/gestao/turmas', methods=['GET', 'POST'])
@app.route('/gestao/turmas.html', methods=['GET', 'POST'])
@app.route('/gestao/turmas-e-filiais', methods=['GET', 'POST'])
@app.route('/gestao/turmas-e-filiais.html', methods=['GET', 'POST'])
@app.route('/gestao_turmas', methods=['GET', 'POST'])
@app.route('/gestao_turmas.html', methods=['GET', 'POST'])
@role_required('instrutor')
def gestao_turmas():
    ensure_class_groups()
    if request.method == 'POST':
        action = request.form.get('action', 'create')
        class_group = db.session.get(ClassGroup, request.form.get('class_id', type=int)) if action == 'update' else ClassGroup()
        if action == 'update' and not class_group:
            flash('Turma não encontrada para edição.', 'error')
            return redirect(url_for('gestao_turmas'))
        name = request.form.get('class_name', '').strip()
        modality = request.form.get('class_modality', '').strip()
        audience = request.form.get('class_audience', '').strip()
        schedules = parse_class_schedules(request.form.get('class_schedule'))
        instructor = request.form.get('class_instructor', '').strip()
        responsible_monitor_id = request.form.get('responsible_monitor_id', type=int)
        responsible_monitor = db.session.get(User, responsible_monitor_id) if responsible_monitor_id else None
        capacity = request.form.get('class_capacity', type=int)
        duration = request.form.get('class_duration', type=int)
        status = request.form.get('class_status', 'ativa')
        location_slug = request.form.get('class_location_slug', 'cajazeiras-sede').strip()

        duplicate = ClassGroup.query.filter(ClassGroup.name == name)
        if action == 'update':
            duplicate = duplicate.filter(ClassGroup.id != class_group.id)
        if (not name or modality not in {'Jiu-Jitsu', 'Boxe', 'Muay Thai', 'MMA'}
                or audience not in {'Adulto', 'Kids', 'Todos'} or not schedules
                or not instructor or not capacity or not 1 <= capacity <= 100
                or duration not in {45, 60, 75, 90, 120}
                or status not in {'ativa', 'lotada', 'rascunho', 'suspensa'}):
            flash('Revise os campos obrigatórios da turma.', 'error')
            return redirect(url_for('gestao_turmas'))
        if duplicate.first():
            flash('Já existe uma turma cadastrada com esse nome.', 'error')
            return redirect(url_for('gestao_turmas'))
        if responsible_monitor_id and (not responsible_monitor or responsible_monitor.role != 'monitor'):
            flash('Selecione um monitor responsável válido.', 'error')
            return redirect(url_for('gestao_turmas'))
        class_group.name = name
        class_group.modality = modality
        class_group.audience = audience
        class_group.schedules = schedules
        class_group.instructor = instructor
        class_group.responsible_monitor = responsible_monitor
        class_group.capacity = capacity
        class_group.duration_minutes = duration
        class_group.status = status
        class_group.location_slug = location_slug
        class_group.publish_public = request.form.get('publish_public') == '1'
        if action == 'create':
            db.session.add(class_group)
        db.session.commit()
        flash(f'Turma {class_group.name} salva com sucesso!', 'success')
        return redirect(url_for('gestao_turmas'))

    search_query = request.args.get('q', '').strip()
    modality_filter = request.args.get('modality', 'todas')
    status_filter = request.args.get('status', 'todos')
    location_filter = request.args.get('location_slug', 'todas')
    query = ClassGroup.query
    if search_query:
        query = query.filter(
            ClassGroup.name.ilike(f'%{search_query}%') |
            ClassGroup.modality.ilike(f'%{search_query}%') |
            ClassGroup.instructor.ilike(f'%{search_query}%') |
            ClassGroup.audience.ilike(f'%{search_query}%')
        )
    if modality_filter != 'todas':
        query = query.filter(ClassGroup.modality == modality_filter)
    if status_filter != 'todos':
        query = query.filter(ClassGroup.status == status_filter)
    if location_filter != 'todas':
        query = query.filter(ClassGroup.location_slug == location_filter)
    classes = query.order_by(ClassGroup.modality, ClassGroup.name).all()

    all_classes = ClassGroup.query.order_by(ClassGroup.id).all()
    checkin_metrics = {
        item.id: {'people': set(), 'records': 0, 'confirmed': 0, 'pending': 0}
        for item in all_classes
    }
    class_ids = list(checkin_metrics)
    if class_ids:
        attendances = Attendance.query.filter(
            Attendance.class_group_id.in_(class_ids),
            Attendance.status.in_({'pendente', 'confirmado'}),
        ).all()
        for attendance in attendances:
            metric = checkin_metrics[attendance.class_group_id]
            identity = (attendance.user.username or str(attendance.user_id)).strip().casefold()
            metric['people'].add(identity)
            metric['records'] += 1
            metric['confirmed' if attendance.status == 'confirmado' else 'pending'] += 1

        bookings = Booking.query.filter(Booking.class_group_id.in_(class_ids)).all()
        for booking in bookings:
            metric = checkin_metrics[booking.class_group_id]
            identity = (booking.login_or_name or f'reserva-{booking.id}').strip().casefold()
            metric['people'].add(identity)
            metric['records'] += 1

    for item in all_classes:
        item.checkin_people = len(checkin_metrics[item.id]['people'])
        item.checkin_records = checkin_metrics[item.id]['records']

    total_capacity = sum(item.capacity for item in all_classes)
    total_enrolled = sum(item.enrolled for item in all_classes)
    all_checkin_people = set().union(*(metric['people'] for metric in checkin_metrics.values())) if checkin_metrics else set()
    overview = {
        'classes': len(all_classes),
        'weekly_sessions': sum(item.weekly_sessions for item in all_classes),
        'enrolled': total_enrolled,
        'occupancy': round(total_enrolled / total_capacity * 100) if total_capacity else 0,
        'waiting': sum(item.waiting for item in all_classes),
        'checkin_people': len(all_checkin_people),
        'checkin_records': sum(metric['records'] for metric in checkin_metrics.values()),
    }

    modalities_smart_metrics = []
    for mod in ['Jiu-Jitsu', 'Boxe', 'Muay Thai', 'MMA']:
        mod_classes = [c for c in all_classes if c.modality == mod]
        mod_capacity = sum(c.capacity for c in mod_classes)
        mod_enrolled = sum(c.enrolled for c in mod_classes)
        mod_waiting = sum(c.waiting for c in mod_classes)
        mod_occupancy = round(mod_enrolled / mod_capacity * 100) if mod_capacity else 0
        mod_metrics = [checkin_metrics[c.id] for c in mod_classes]
        mod_people = set().union(*(metric['people'] for metric in mod_metrics)) if mod_metrics else set()
        confirmed_attendances = sum(metric['confirmed'] for metric in mod_metrics)
        pending_attendances = sum(metric['pending'] for metric in mod_metrics)
        checkin_records = sum(metric['records'] for metric in mod_metrics)
        
        enrolled_user_ids = {
            e.user_id for c in mod_classes for e in c.enrollments
            if e.active and not e.is_demo
        }
        if enrolled_user_ids:
            enrolled_users = User.query.filter(User.id.in_(enrolled_user_ids)).all()
            paid_count = sum(1 for u in enrolled_users if u.payment_status == 'Em Dia' or u.monthly_fee_exempt)
            adimplencia = round(paid_count / len(enrolled_users) * 100)
            decided_attendances = Attendance.query.filter(
                Attendance.user_id.in_(enrolled_user_ids),
                Attendance.modality == mod,
                Attendance.status.in_({'confirmado', 'negado'}),
            ).all()
            attendance_rate = round(
                sum(1 for item in decided_attendances if item.status == 'confirmado')
                / len(decided_attendances) * 100
            ) if decided_attendances else None
        else:
            adimplencia = None
            attendance_rate = None

        modalities_smart_metrics.append({
            'name': mod,
            'classes_count': len(mod_classes),
            'capacity': mod_capacity,
            'enrolled': mod_enrolled,
            'occupancy': mod_occupancy,
            'waiting': mod_waiting,
            'adimplencia': adimplencia,
            'attendance_rate': attendance_rate,
            'checkin_people': len(mod_people),
            'checkin_records': checkin_records,
            'confirmed_attendances': confirmed_attendances,
            'pending_attendances': pending_attendances,
            'icon': get_icon_for_modality(mod)
        })

    return render_template(
        'gestao_turmas.html', page_title='Gestão de Turmas e Filiais', classes=classes, overview=overview,
        modalities_smart=modalities_smart_metrics, search_query=search_query,
        modality_filter=modality_filter, status_filter=status_filter, location_filter=location_filter,
        locations_dict=get_locations_dict(),
        monitors=User.query.filter_by(role='monitor').order_by(User.name).all(),
    )

DEFAULT_MODALITY_ICONS = {
    'Jiu-Jitsu': 'jiujitsu_kimono',
    'Boxe': 'boxing_gloves',
    'Muay Thai': 'hand_wrap',
    'MMA': 'mma_glove'
}

def get_modality_icons_path():
    return os.path.join(app.instance_path, 'modality_icons.json')

def get_modality_icons():
    filepath = get_modality_icons_path()
    icons = dict(DEFAULT_MODALITY_ICONS)
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                saved = json.load(f)
                if isinstance(saved, dict):
                    icons.update(saved)
        except Exception as e:
            app.logger.error(f"Erro ao ler modality_icons.json: {e}")
    return icons

def save_modality_icons(icons_dict):
    filepath = get_modality_icons_path()
    os.makedirs(app.instance_path, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(icons_dict, f, ensure_ascii=False, indent=2)

def get_icon_for_modality(modality_name):
    icons = get_modality_icons()
    if modality_name in icons:
        return icons[modality_name]
    mod_lower = str(modality_name).lower()
    for k, v in icons.items():
        if k.lower() in mod_lower or mod_lower in k.lower():
            return v
    return 'award'

def get_class_group_icons_path():
    return os.path.join(app.instance_path, 'class_group_icons.json')

def get_class_group_icons():
    filepath = get_class_group_icons_path()
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                saved = json.load(f)
                if isinstance(saved, dict):
                    return saved
        except Exception as e:
            app.logger.error(f"Erro ao ler class_group_icons.json: {e}")
    return {}

def save_class_group_icons(icons_dict):
    filepath = get_class_group_icons_path()
    os.makedirs(app.instance_path, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(icons_dict, f, ensure_ascii=False, indent=2)

def get_icon_for_class_group(class_group):
    cg_icons = get_class_group_icons()
    cg_id_str = str(class_group.id) if hasattr(class_group, 'id') else ''
    if cg_id_str and cg_id_str in cg_icons:
        return cg_icons[cg_id_str]
    if hasattr(class_group, 'name') and class_group.name in cg_icons:
        return cg_icons[class_group.name]
    return get_icon_for_modality(getattr(class_group, 'modality', ''))

@app.route('/gestao/icones', methods=['GET', 'POST'])
@app.route('/gestao_icones.html', methods=['GET', 'POST'])
@role_required('instrutor')
def gestao_icones():
    ensure_class_groups()
    if request.method == 'POST':
        action = request.form.get('action', '')
        if action == 'save_modality_icons':
            mod_icons = get_modality_icons()
            cg_icons = get_class_group_icons()

            for key, val in request.form.items():
                val_str = val.strip()
                if key.startswith('icon_mod_'):
                    mod_name = key[9:]
                    if mod_name and val_str:
                        mod_icons[mod_name] = val_str
                elif key.startswith('icon_class_'):
                    class_id = key[11:]
                    if class_id and val_str:
                        cg_icons[class_id] = val_str
            
            save_modality_icons(mod_icons)
            save_class_group_icons(cg_icons)
            flash('✨ Ícones das modalidades e turmas atualizados com sucesso!', 'success')
            return redirect(url_for('gestao_icones'))

    all_class_groups = ClassGroup.query.order_by(ClassGroup.name).all()
    modalities_in_use = set(c.modality for c in all_class_groups if c.modality)
    
    locations = Location.query.all()
    for loc in locations:
        try:
            mods = json.loads(loc.modalities_json or '[]')
            for m in mods:
                if m: modalities_in_use.add(m)
        except Exception:
            pass
    current_icons = get_modality_icons()
    current_cg_icons = get_class_group_icons()
    
    modality_items = []
    for mod_name in sorted(modalities_in_use):
        classes_using = [c for c in all_class_groups if c.modality == mod_name]
        icon_name = current_icons.get(mod_name, get_icon_for_modality(mod_name))
        modality_items.append({
            'name': mod_name,
            'icon': icon_name,
            'classes_count': len(classes_using),
            'classes_sample': [c.name for c in classes_using[:3]]
        })

    turma_items = []
    for cg in all_class_groups:
        cg_icon = current_cg_icons.get(str(cg.id), get_icon_for_class_group(cg))
        turma_items.append({
            'id': cg.id,
            'name': cg.name,
            'modality': cg.modality,
            'audience': cg.audience,
            'icon': cg_icon
        })

    preset_icons = [
        {'name': 'jiujitsu_kimono', 'label': '🥋 Kimono Jiu-Jitsu', 'icon': 'jiujitsu_kimono'},
        {'name': 'female_fighter', 'label': '🥋 Atleta Feminina / Jiu-Jitsu Feminino', 'icon': 'female_fighter'},
        {'name': 'male_fighter', 'label': '🎽 Atleta Masculino / Boxe & Muay Thai', 'icon': 'male_fighter'},
        {'name': 'headgear_full', 'label': '⛑️ Capacete de Proteção / Headgear Full', 'icon': 'headgear_full'},
        {'name': 'headgear_padding', 'label': '🥊 Capacete Sparring / Protetor Almofadado', 'icon': 'headgear_padding'},
        {'name': 'groin_guard', 'label': '🛡️ Protetor / Coquilha / Shield', 'icon': 'groin_guard'},
        {'name': 'mma_glove', 'label': '🥊 Luva MMA (Dedo Aberto)', 'icon': 'mma_glove'},
        {'name': 'boxing_gloves', 'label': '🥊 Luvas de Boxe Penduradas', 'icon': 'boxing_gloves'},
        {'name': 'boxing_upright', 'label': '🥊 Luvas de Boxe Par Frontal', 'icon': 'boxing_upright'},
        {'name': 'hand_wrap', 'label': '🥊 Mão Enfaixada / Bandagem Muay Thai', 'icon': 'hand_wrap'},
        {'name': 'glove_touch', 'label': '🥊 Touch de Luvas / Sparring', 'icon': 'glove_touch'},
        {'name': 'handshake_clasp', 'label': '🤝 Pegada / Respeito / União', 'icon': 'handshake_clasp'},
        {'name': 'running_shoe', 'label': '👟 Tênis Corrida / Funcional', 'icon': 'running_shoe'},
        {'name': 'kids_running', 'label': '🏃 Crianças Correndo / Turma Kids', 'icon': 'kids_running'},
        {'name': 'baby_blocks', 'label': '👶 Criança com Blocos / Turma Baby', 'icon': 'baby_blocks'},
        {'name': 'signed_contract', 'label': '📝 Contrato Assinado / Matrícula', 'icon': 'signed_contract'},
        {'name': 'student_file', 'label': '📋 Ficha do Aluno / Cadastro', 'icon': 'student_file'},
        {'name': 'partnership_agreement', 'label': '🤝 Parceria / Acordo / Família', 'icon': 'partnership_agreement'},
        {'name': 'hand_payment', 'label': '💵 Pagamento / Mensalidade', 'icon': 'hand_payment'}
    ]

    overview = {
        'total_modalities': len(modality_items),
        'active_classes': len(all_class_groups),
        'total_presets': len(preset_icons)
    }

    return render_template(
        'gestao_icones.html',
        page_title='Gestão de Ícones e Modalidades',
        modality_items=modality_items,
        turma_items=turma_items,
        preset_icons=preset_icons,
        overview=overview
    )

@app.route('/gestao/turmas/<int:class_id>')
@role_required('instrutor')
def gestao_turma_detalhes(class_id):
    ensure_class_groups()
    class_group = db.get_or_404(ClassGroup, class_id)
    today = datetime.now().date()
    selected_year = request.args.get('year', type=int) or today.year
    if selected_year < today.year - 5 or selected_year > today.year + 1:
        selected_year = today.year
    enrollments = [item for item in class_group.enrollments if item.active]
    enrollments.sort(key=lambda item: item.user.name)
    user_ids = [item.user_id for item in enrollments]
    payments = MonthlyPayment.query.filter(
        MonthlyPayment.user_id.in_(user_ids), MonthlyPayment.year == selected_year
    ).all() if user_ids else []
    payment_lookup = {(item.user_id, item.month): item for item in payments}
    month_limit = today.month if selected_year == today.year else (12 if selected_year < today.year else 0)
    monthly_financial = []
    expected_total = received_total = overdue_total = 0.0
    for month in range(1, 13):
        row = {'month': month, 'expected': 0.0, 'received': 0.0, 'overdue': 0.0, 'payments': 0}
        if month <= month_limit:
            for enrollment in enrollments:
                user = enrollment.user
                if selected_year == today.year and user.start_month and month < user.start_month:
                    continue
                payment = payment_lookup.get((user.id, month))
                if payment and payment.status == 'pago':
                    amount = float(payment.amount)
                    row['expected'] += amount
                    row['received'] += amount
                    row['payments'] += 1
                elif not user.is_fee_exempt_for(selected_year, month):
                    amount = float(payment.amount) if payment else user.get_plan_price()
                    row['expected'] += amount
                    if payment and payment.status == 'atrasado':
                        row['overdue'] += amount
        expected_total += row['expected']
        received_total += row['received']
        overdue_total += row['overdue']
        monthly_financial.append(row)

    attendance_start = today - timedelta(days=89)
    attendance_records = Attendance.query.filter(
        Attendance.user_id.in_(user_ids), Attendance.training_date >= attendance_start
    ).all() if user_ids else []
    attendance_records = [item for item in attendance_records if (
        item.class_group_id == class_group.id or
        (item.class_group_id is None and item.modality == class_group.modality)
    )]
    confirmed_count = sum(1 for item in attendance_records if item.status == 'confirmado')
    denied_count = sum(1 for item in attendance_records if item.status == 'negado')
    pending_count = sum(1 for item in attendance_records if item.status == 'pendente')
    decided_count = confirmed_count + denied_count
    attendance_rate = round(confirmed_count / decided_count * 100) if decided_count else None

    class_attendances = Attendance.query.filter_by(class_group_id=class_group.id).all()
    class_bookings = Booking.query.filter_by(class_group_id=class_group.id).all()
    booking_logins = {
        (item.login_or_name or '').strip().casefold() for item in class_bookings
        if (item.login_or_name or '').strip()
    }
    booking_users = User.query.filter(func.lower(User.username).in_(booking_logins)).all() if booking_logins else []
    booking_user_lookup = {item.username.strip().casefold(): item for item in booking_users}
    checkin_rows = []
    checkin_people_keys = set()
    for attendance in class_attendances:
        person_key = attendance.user.username.strip().casefold()
        checkin_people_keys.add(person_key)
        checkin_rows.append({
            'person_name': attendance.user.name,
            'username': attendance.user.username,
            'date': attendance.training_date,
            'time': attendance.created_at.strftime('%H:%M') if attendance.created_at else None,
            'source': 'Presença',
            'status': attendance.status,
            'status_label': {'confirmado': 'Confirmada', 'pendente': 'Pendente', 'negado': 'Negada'}.get(attendance.status, attendance.status),
        })
    for booking in class_bookings:
        raw_identity = (booking.login_or_name or '').strip()
        person_key = raw_identity.casefold() or f'reserva-{booking.id}'
        booking_user = booking_user_lookup.get(person_key)
        checkin_people_keys.add(person_key)
        checkin_rows.append({
            'person_name': booking_user.name if booking_user else raw_identity or 'Pessoa não identificada',
            'username': booking_user.username if booking_user else raw_identity,
            'date': booking.class_date or (booking.created_at.date() if booking.created_at else None),
            'time': booking.class_time or (booking.created_at.strftime('%H:%M') if booking.created_at else None),
            'source': 'Landing page',
            'status': 'reserva',
            'status_label': 'Check-in registrado',
        })
    checkin_rows.sort(key=lambda item: (item['date'] or date.min, item['time'] or ''), reverse=True)

    member_rows = []
    for enrollment in enrollments:
        user = enrollment.user
        user_payments = [item for item in payments if item.user_id == user.id]
        user_attendance = [item for item in attendance_records if item.user_id == user.id]
        user_confirmed = sum(1 for item in user_attendance if item.status == 'confirmado')
        user_denied = sum(1 for item in user_attendance if item.status == 'negado')
        user_decided = user_confirmed + user_denied
        member_rows.append({
            'user': user, 'is_demo': enrollment.is_demo,
            'received': sum(float(item.amount) for item in user_payments if item.status == 'pago'),
            'overdue': user.get_overdue_details()['total_debt'],
            'confirmed': user_confirmed,
            'attendance_rate': round(user_confirmed / user_decided * 100) if user_decided else None,
        })
    return render_template(
        'gestao_turma_detalhes.html', page_title=f'Turma • {class_group.name}',
        class_group=class_group, enrollments=enrollments, member_rows=member_rows,
        selected_year=selected_year, years=range(today.year - 2, today.year + 1),
        expected_total=expected_total, received_total=received_total, overdue_total=overdue_total,
        receipt_rate=round(received_total / expected_total * 100) if expected_total else 0,
        monthly_financial=monthly_financial, confirmed_count=confirmed_count,
        denied_count=denied_count, pending_count=pending_count, attendance_rate=attendance_rate,
        demo_count=sum(1 for item in enrollments if item.is_demo),
        checkin_rows=checkin_rows, checkin_people_count=len(checkin_people_keys),
    )

@app.route('/dar-baixa-mensalidade/<int:user_id>', methods=['POST'])
@login_required
def dar_baixa_mensalidade(user_id):
    if session.get('user_role') not in {'instrutor', 'monitor'}:
        flash('Apenas instrutores e monitores podem dar baixa na mensalidade.', 'error')
        return redirect(request.referrer or url_for('mensalidades_admin'))

    current_user = db.session.get(User, session.get('user_id'))
    student = db.session.get(User, user_id)
    if not student:
        flash('Aluno não encontrado.', 'error')
        return redirect(request.referrer or url_for('mensalidades_admin'))

    if not student.can_be_managed_by(current_user):
        flash('Acesso negado: monitores só podem dar baixa em alunos da sua própria turma.', 'error')
        return redirect(request.referrer or url_for('mensalidades_admin'))

    current_date = datetime.now()
    current_month = current_date.month
    current_year = current_date.year

    student.set_month_status(f'{current_month:02d}', 'pago', current_year)
    student.payment_status = 'Em Dia'
    db.session.commit()

    flash(f'✅ Mensalidade de {student.name} confirmada com sucesso! Status alterado para Em Dia.', 'success')
    return redirect(request.referrer or url_for('mensalidades_admin'))

@app.route('/api/update_month_status', methods=['POST'])
@login_required
def api_update_month_status():
    if session.get('user_role') not in {'instrutor', 'monitor'}:
        flash('Somente monitores e instrutores podem atualizar o status da mensalidade.', 'error')
        return redirect(request.referrer or url_for('mensalidades_admin'))

    current_user = db.session.get(User, session.get('user_id'))
    user_id = request.form.get('user_id')
    month = request.form.get('month')
    status = request.form.get('status')
    
    user = db.session.get(User, user_id)
    year = request.form.get('year', type=int) or datetime.now().year

    if not user:
        flash('Aluno não encontrado.', 'error')
        return redirect(request.referrer or url_for('mensalidades_admin'))

    if not user.can_be_managed_by(current_user):
        flash('Somente o monitor responsável pela turma deste aluno ou instrutores podem alterar a mensalidade.', 'error')
        return redirect(request.referrer or url_for('mensalidades_admin'))

    if month and month.isdigit() and 1 <= int(month) <= 12 and status in ['pago', 'atrasado', 'futuro']:
        user.set_month_status(month, status, year)
        if status == 'pago':
            user.payment_status = 'Em Dia'
        db.session.commit()
        flash(f'Baixa realizada! Mês {month} de {user.name} alterado para {status.upper()}.', 'success')
    
    referrer = request.referrer or url_for('mensalidades_admin')
    return redirect(referrer)

def _report_periods(start_value, end_value):
    try:
        start = datetime.strptime(start_value, '%Y-%m').date().replace(day=1)
        end = datetime.strptime(end_value, '%Y-%m').date().replace(day=1)
    except (TypeError, ValueError):
        raise ValueError('Informe um período válido para o relatório.')
    total_months = (end.year - start.year) * 12 + end.month - start.month
    if total_months < 0:
        raise ValueError('O período final deve ser igual ou posterior ao inicial.')
    if total_months > 59:
        raise ValueError('O relatório pode abranger no máximo 60 meses.')
    periods = []
    year, month = start.year, start.month
    while (year, month) <= (end.year, end.month):
        periods.append((year, month))
        month += 1
        if month == 13:
            year, month = year + 1, 1
    return periods

def _financial_report_users(form):
    if form.get('scope', 'current') == 'all':
        return User.query.order_by(User.name.asc()).all(), 'Todos os alunos'
    query = User.query
    due_filter = form.get('filter_day', 'todos')
    status_filter = form.get('filter_status', 'todos')
    modality_filter = form.get('filter_modality', 'todos')
    search_query = form.get('filter_query', '').strip()
    if due_filter in {'5', '15', '25'}:
        query = query.filter(User.due_date == due_filter)
    if modality_filter != 'todos':
        query = query.filter(User.plan.ilike(f'%{modality_filter}%'))
    if status_filter == 'pago':
        query = query.filter(User.payment_status == 'Em Dia', User.monthly_fee_exempt.is_(False))
    elif status_filter == 'pendente':
        query = query.filter(User.payment_status == 'Pendente', User.monthly_fee_exempt.is_(False))
    elif status_filter == 'isento':
        query = query.filter(User.monthly_fee_exempt.is_(True))
    if search_query:
        query = query.filter(
            (User.name.ilike(f'%{search_query}%')) |
            (User.username.ilike(f'%{search_query}%')) |
            (User.cpf.ilike(f'%{search_query}%')) |
            (User.plan.ilike(f'%{search_query}%'))
        )
    return query.order_by(User.name.asc()).all(), 'Filtros atuais da tela'

def _clean_report_text(value):
    cleaned = str(value or '').replace('|', '/').replace('\n', ' ')
    cleaned = re.sub(r'[\U00010000-\U0010ffff\u2600-\u27bf\u200d\ufe0f]', '', cleaned)
    return ' '.join(cleaned.split())

def _build_financial_report(users, periods, scope_label, generated_by):
    today = datetime.now()
    status_labels = {
        'pago': 'Pago', 'atrasado': 'Em atraso', 'futuro': 'A vencer',
        'sem_registro': 'Sem registro', 'nao_iniciado': 'Não iniciado', 'isento': 'Isento'
    }
    summary_rows = []
    detail_rows = []
    exempt_user_ids = set()
    totals = {'expected': 0.0, 'received': 0.0, 'overdue': 0.0, 'future': 0.0, 'unrecorded': 0.0}

    for year, month in periods:
        row = {'period': f'{month:02d}/{year}', 'students': 0, 'exempt': 0, 'expected': 0.0,
               'received': 0.0, 'overdue': 0.0, 'future': 0.0, 'unrecorded': 0.0}
        for user in users:
            plan_amount = user.get_plan_price()
            payment = next((item for item in user.payments if item.year == year and item.month == month), None)
            start_month = user.start_month if user.start_month and 1 <= user.start_month <= 12 else 1
            if payment and payment.status == 'pago':
                status = 'pago'
            elif user.is_fee_exempt_for(year, month):
                status = 'isento'
            elif year == today.year and month < start_month:
                status = 'nao_iniciado'
            elif payment:
                status = payment.status
            elif (year, month) > (today.year, today.month):
                status = 'futuro'
            elif year == today.year:
                schedule = {int(item['month']): item['status'] for item in user.get_month_schedule(today.month, year)}
                status = schedule.get(month, 'nao_iniciado')
            else:
                status = 'sem_registro'

            if status in {'nao_iniciado', 'isento'}:
                report_amount = 0.0
            elif payment:
                report_amount = float(payment.amount)
            else:
                report_amount = plan_amount
            if status != 'nao_iniciado':
                row['students'] += 1
                row['expected'] += report_amount
            if status == 'isento':
                row['exempt'] += 1
                exempt_user_ids.add(user.id)
            elif status == 'pago':
                row['received'] += report_amount
            elif status == 'atrasado':
                row['overdue'] += report_amount
            elif status == 'futuro':
                row['future'] += report_amount
            elif status == 'sem_registro':
                row['unrecorded'] += report_amount

            detail_rows.append({
                'period': row['period'],
                'student': _clean_report_text(user.name),
                'username': _clean_report_text(user.username),
                'contact': _clean_report_text(f'({user.ddd}) {user.phone}'),
                'plan': _clean_report_text(user.plan.split('—')[0]),
                'due_date': user.due_date,
                'status': status,
                'status_label': status_labels[status],
                'amount': report_amount,
                'paid_at': payment.paid_at.strftime('%d/%m/%Y') if payment and payment.paid_at else '',
            })
        summary_rows.append(row)
        for key in totals:
            totals[key] += row[key]

    start_year, start_month = periods[0]
    end_year, end_month = periods[-1]
    receipt_rate = (totals['received'] / totals['expected'] * 100) if totals['expected'] else 0.0
    return {
        'generated_at': today.strftime('%d/%m/%Y às %H:%M'),
        'period_label': f'{start_month:02d}/{start_year} a {end_month:02d}/{end_year}',
        'scope_label': scope_label,
        'student_count': len(users),
        'exempt_count': len(exempt_user_ids),
        'generated_by': _clean_report_text(generated_by.name),
        'generated_by_username': _clean_report_text(generated_by.username),
        'generated_by_role': {'instrutor': 'Instrutor', 'monitor': 'Monitor financeiro'}.get(
            generated_by.role, generated_by.role.capitalize()
        ),
        'summary_rows': summary_rows,
        'detail_rows': detail_rows,
        'totals': totals,
        'receipt_rate': receipt_rate,
    }

@app.route('/relatorios/mensalidades/exportar', methods=['POST'])
@role_required('instrutor')
def exportar_relatorio_mensalidades():
    report_format = request.form.get('format', 'pdf').lower()
    report_type = request.form.get('report_type', 'summary').lower()
    if report_format not in {'pdf', 'xlsx'} or report_type not in {'summary', 'detailed'}:
        return jsonify({'error': 'Formato ou nível de detalhe inválido.'}), 400
    try:
        periods = _report_periods(request.form.get('period_start'), request.form.get('period_end'))
    except ValueError as error:
        return jsonify({'error': str(error)}), 400

    users, scope_label = _financial_report_users(request.form)
    generated_by = db.session.get(User, session['user_id'])
    report = _build_financial_report(users, periods, scope_label, generated_by)
    detailed = report_type == 'detailed'
    date_slug = f'{periods[0][0]}-{periods[0][1]:02d}_a_{periods[-1][0]}-{periods[-1][1]:02d}'

    if report_format == 'xlsx':
        response = send_file(
            financial_report_to_xlsx(report, detailed),
            as_attachment=True,
            download_name=f'mensalidades_{report_type}_{date_slug}.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            max_age=0,
        )
        response.headers['X-Report-Workflow'] = 'XLSX'
        return response

    markdown_content = build_financial_markdown(report, detailed)
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.md', encoding='utf-8') as markdown_file:
        markdown_file.write(markdown_content)
        markdown_file.flush()
        markdown_file.seek(0)
        pdf_file = markdown_to_pdf(markdown_file.read())
    response = send_file(
        pdf_file,
        as_attachment=True,
        download_name=f'mensalidades_{report_type}_{date_slug}.pdf',
        mimetype='application/pdf',
        max_age=0,
    )
    response.headers['X-Report-Workflow'] = 'Markdown-to-PDF'
    return response

@app.route('/mensalidades_admin', methods=['GET', 'POST'])
@app.route('/mensalidades_admin.html', methods=['GET', 'POST'])
@role_required('instrutor')
def mensalidades_admin():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'reset_student_password':
            user = db.session.get(User, request.form.get('user_id', type=int))
            if not user:
                flash('Usuário não encontrado para redefinição de senha.', 'error')
            else:
                user.set_password('bemvindo')
                user.must_change_password = True
                user.password_reset_by_username = session.get('username') or 'sistema'
                user.password_reset_at = datetime.now()
                db.session.commit()
                flash(f'Senha de {user.name} redefinida para “bemvindo”. A troca será obrigatória no próximo acesso.', 'success')
        elif action == 'toggle_exemption':
            user = db.session.get(User, request.form.get('user_id', type=int))
            if user:
                is_exempt = request.form.get('is_exempt') == '1'
                current_date = datetime.now()
                active_exemption = next((item for item in user.fee_exemptions if item.end_year is None), None)
                if is_exempt and not active_exemption:
                    db.session.add(MonthlyFeeExemption(
                        user_id=user.id,
                        start_year=current_date.year,
                        start_month=current_date.month,
                        granted_by_username=session.get('username') or 'sistema',
                        granted_at=current_date,
                    ))
                elif not is_exempt and active_exemption:
                    active_exemption.end_year = current_date.year
                    active_exemption.end_month = current_date.month
                    active_exemption.revoked_by_username = session.get('username') or 'sistema'
                    active_exemption.revoked_at = current_date
                user.monthly_fee_exempt = is_exempt
                user.fee_exempted_by_username = session.get('username') if is_exempt else None
                user.fee_exempted_at = current_date if is_exempt else None
                db.session.commit()
                if is_exempt:
                    flash(f'{user.name} agora está isento(a) de mensalidade.', 'success')
                else:
                    flash(f'Isenção de {user.name} removida. A cobrança mensal voltou a ser contabilizada.', 'info')
        elif action == 'update_student_plan':
            user = db.session.get(User, request.form.get('user_id', type=int))
            plan_key = request.form.get('plan_id', '').strip()
            is_private_class = plan_key == '__private_class__'
            plan = db.session.get(Plan, int(plan_key)) if plan_key.isdigit() else None
            private_instructor = User.query.filter_by(
                username=request.form.get('private_instructor', '').strip()
            ).first() if is_private_class else None
            training_days = request.form.get('training_days', '').strip()
            selected_modalities = list(dict.fromkeys(
                item for item in request.form.getlist('selected_modalities')
                if item in {'Jiu-Jitsu', 'Boxe', 'Muay Thai', 'MMA'}
            ))
            if not user or user.role != 'aluno':
                flash('Aluno não encontrado para alteração do plano.', 'error')
            elif is_private_class and (not private_instructor or private_instructor.role not in {'professor', 'instrutor', 'monitor'}):
                flash('Escolha um professor ou monitor válido para a aula particular.', 'error')
            elif not is_private_class and (not plan or 'passe livre' in plan.name.casefold()):
                flash('Selecione um plano válido do catálogo atual.', 'error')
            else:
                expected_combo_count = plan.get_selection_count() if plan else 0
                if expected_combo_count and len(selected_modalities) != expected_combo_count:
                    flash(f'Este combo exige {expected_combo_count} modalidades diferentes.', 'error')
                    return redirect(url_for('mensalidades_admin'))
                if plan and not expected_combo_count:
                    selected_modalities = plan.get_modalities()
                if plan and plan.requires_all_days():
                    training_days = 'todos'
                training_day_labels = {
                    'seg-qua-sex': 'Seg, Qua, Sex', 'ter-qui': 'Ter, Qui', 'todos': 'Todos os dias'
                }
                if training_days not in training_day_labels:
                    flash('Selecione os dias de treino do novo plano.', 'error')
                    return redirect(url_for('mensalidades_admin'))
                old_plan = user.plan
                if is_private_class:
                    user.plan = f'Aula Particular com {private_instructor.name} • {training_day_labels[training_days]}'
                else:
                    user.plan = f'{plan.name} • {training_day_labels[training_days]} — {plan.get_price_for_schedule(training_days)}'
                user.selected_modalities = ', '.join(selected_modalities) if selected_modalities else None
                db.session.commit()
                new_plan_name = 'Aula Particular' if is_private_class else plan.name
                flash(f'Plano de {user.name} alterado de “{old_plan.split("—")[0].strip()}” para “{new_plan_name}”.', 'success')
        elif action == 'update_month':
            user_id = request.form.get('user_id')
            month = request.form.get('month')
            status = request.form.get('status')
            user = db.session.get(User, user_id)
            if user and month and month.isdigit() and 1 <= int(month) <= 12 and status in {'pago', 'atrasado', 'futuro'}:
                user.set_month_status(month, status)
                db.session.commit()
                flash(f'Mensalidade do Mês {month} de {user.name} atualizada para {status.upper()}!', 'success')
        else:
            user_id = request.form.get('user_id')
            new_status = request.form.get('payment_status')
            new_due_date = request.form.get('due_date')
            user = db.session.get(User, user_id)
            if user:
                if new_status in {'Em Dia', 'Pendente'}: user.payment_status = new_status
                proration_msg = ""
                if new_due_date and new_due_date.isdigit() and 1 <= int(new_due_date) <= 28:
                    if str(new_due_date) != str(user.due_date):
                        res = change_user_due_date_with_proration(user, new_due_date)
                        if res and res.get('days', 0) > 0 and res.get('amount', 0) > 0:
                            proration_msg = f" (Acréscimo proporcional: +{res['days']} dia(s) = R$ {res['amount']:.2f})"
                db.session.commit()
                flash(f'Vencimento de {user.name} alterado para o Dia {user.due_date}{proration_msg}! Status: {user.payment_status}', 'success')
        
        filter_day = request.args.get('day', 'todos')
        search_query = request.args.get('q', '')
        status_filter = request.args.get('status', 'todos')
        modality_filter = request.args.get('modality', 'todos')
        return redirect(url_for('mensalidades_admin', day=filter_day, q=search_query, status=status_filter, modality=modality_filter))

    filter_day = request.args.get('day', 'todos')
    search_query = request.args.get('q', '').strip()
    status_filter = request.args.get('status', 'todos')
    modality_filter = request.args.get('modality', 'todos')

    query = User.query

    if filter_day == 'proximos_5_dias':
        today_day = datetime.now().day
        next_5_days = [str((today_day + i - 1) % 28 + 1) for i in range(5)]
        query = query.filter(User.due_date.in_(next_5_days))
    elif filter_day and filter_day.isdigit() and 1 <= int(filter_day) <= 28:
        query = query.filter(User.due_date == filter_day)

    if modality_filter != 'todos':
        query = query.filter(User.plan.ilike(f'%{modality_filter}%'))

    if search_query:
        query = query.filter(
            (User.name.ilike(f'%{search_query}%')) |
            (User.username.ilike(f'%{search_query}%')) |
            (User.cpf.ilike(f'%{search_query}%')) |
            (User.plan.ilike(f'%{search_query}%'))
        )

    if status_filter == 'pago':
        query = query.filter(User.payment_status == 'Em Dia', User.monthly_fee_exempt.is_(False))
    elif status_filter == 'pendente':
        query = query.filter(User.payment_status == 'Pendente', User.monthly_fee_exempt.is_(False))
    elif status_filter == 'isento':
        query = query.filter(User.monthly_fee_exempt.is_(True))

    users_list = query.order_by(User.id.asc()).all()

    total_count = User.query.count()
    today_day = datetime.now().day
    next_5_days = [str((today_day + i - 1) % 28 + 1) for i in range(5)]
    due_soon_count = User.query.filter(User.due_date.in_(next_5_days), User.monthly_fee_exempt.is_(False)).count()
    paid_count = User.query.filter_by(payment_status='Em Dia', monthly_fee_exempt=False).count()
    pending_count = User.query.filter_by(payment_status='Pendente', monthly_fee_exempt=False).count()
    exempt_count = User.query.filter_by(monthly_fee_exempt=True).count()
    current_period = datetime.now()
    available_plans = Plan.query.filter(~Plan.name.ilike('%passe livre%')).order_by(Plan.category, Plan.name).all()
    student_plan_catalog = {
        'individual': [
            {'id': plan.id, 'name': plan.name, 'label': plan.get_modalities()[0], 'price': plan.price, 'category': plan.category,
             'prices': {key: plan.get_price_for_schedule(key) for key in ('ter-qui', 'seg-qua-sex', 'todos')},
             'modalities': plan.get_modalities(), 'selection_count': plan.get_selection_count(),
             'force_all_days': plan.requires_all_days()}
            for plan in available_plans if plan.category == 'Planos Individuais'
            and len(plan.get_modalities()) == 1
        ],
        'special': [
            {'id': plan.id, 'name': plan.name, 'label': plan.name, 'price': plan.price, 'category': plan.category,
             'prices': {key: plan.get_price_for_schedule(key) for key in ('ter-qui', 'seg-qua-sex', 'todos')},
             'modalities': plan.get_modalities(), 'selection_count': plan.get_selection_count(),
             'force_all_days': plan.requires_all_days(), 'combo_count': plan.get_selection_count()}
            for plan in available_plans if plan.category != 'Planos Individuais'
        ],
    }
    student_plan_catalog['special'].append({
        'id': '__private_class__', 'name': 'Aula Particular', 'label': 'Aula Particular',
        'prices': {'ter-qui': 'A combinar', 'seg-qua-sex': 'A combinar', 'todos': 'A combinar'},
        'modalities': [], 'selection_count': 0, 'force_all_days': False, 'private_class': True,
    })
    plan_professionals = sorted(
        User.query.filter(User.role.in_({'professor', 'instrutor', 'monitor'})).all(),
        key=lambda professional: (0 if professional.role in {'professor', 'instrutor'} else 1,
                                  professional.name.casefold()),
    )

    return render_template(
        'mensalidades_admin.html',
        page_title='Gestão de Mensalidades (30 Alunos)',
        users=users_list,
        filter_day=filter_day,
        search_query=search_query,
        status_filter=status_filter,
        modality_filter=modality_filter,
        total_count=total_count,
        due_soon_count=due_soon_count,
        paid_count=paid_count,
        pending_count=pending_count,
        exempt_count=exempt_count,
        report_period_start=f'{current_period.year}-01',
        report_period_end=f'{current_period.year}-{current_period.month:02d}',
        available_plans=available_plans, student_plan_catalog=student_plan_catalog,
        plan_professionals=plan_professionals,
    )

@app.route('/gestao', methods=['GET', 'POST'])
@app.route('/gestao.html', methods=['GET', 'POST'])
@role_required('instrutor')
def gestao_privilegios():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        new_role = request.form.get('new_role')
        user = db.session.get(User, user_id)
        if user and new_role in ['aluno', 'monitor', 'instrutor']:
            if user.role == 'instrutor' and new_role != 'instrutor' and User.query.filter_by(role='instrutor').count() == 1:
                flash('Não é possível remover o último instrutor do sistema.', 'error')
                return redirect(url_for('gestao_privilegios'))
            user.role = new_role
            db.session.commit()
            flash(f'Privilégio de {user.name} atualizado para: {new_role.upper()}!', 'success')
            if session.get('user_id') == user.id:
                session['user_role'] = new_role
        return redirect(url_for('gestao_privilegios'))

    users_list = User.query.order_by(User.id.asc()).all()
    return render_template('gestao.html', page_title='Gestão de Privilégios & Permissões', users=users_list)

@app.route('/gestao/graduacoes', methods=['GET', 'POST'])
@app.route('/gestao/graduacoes.html', methods=['GET', 'POST'])
@role_required('instrutor')
def gestao_graduacoes():
    if request.method == 'POST':
        user = db.session.get(User, request.form.get('user_id', type=int))
        new_color = request.form.get('belt_color', '').strip().lower()
        new_degree = request.form.get('belt_degree', type=int)
        notes = request.form.get('notes', '').strip()
        try:
            graduation_date = datetime.strptime(request.form.get('graduation_date', ''), '%Y-%m-%d').date()
        except ValueError:
            graduation_date = None
        if not user or new_color not in BELT_COLORS or new_degree is None or not 0 <= new_degree <= 4:
            flash('Aluno, faixa ou grau inválido.', 'error')
            return redirect(url_for('gestao_graduacoes'))
        if not graduation_date or graduation_date > datetime.now().date():
            flash('Informe uma data de graduação válida, sem usar uma data futura.', 'error')
            return redirect(url_for('gestao_graduacoes'))
        if len(notes) > 300:
            flash('As observações devem ter no máximo 300 caracteres.', 'error')
            return redirect(url_for('gestao_graduacoes'))
        if user.belt_color == new_color and user.belt_degree == new_degree:
            flash('A faixa e o grau informados já são os atuais deste aluno.', 'warning')
            return redirect(url_for('gestao_graduacoes'))
        record = GraduationRecord(
            user_id=user.id, previous_belt_color=user.belt_color,
            previous_belt_degree=user.belt_degree, new_belt_color=new_color,
            new_belt_degree=new_degree, graduation_date=graduation_date,
            notes=notes or None, updated_by_username=session.get('username', ''),
        )
        user.belt_color, user.belt_degree = new_color, new_degree
        db.session.add(record)
        db.session.commit()
        flash(f'Graduação de {user.name} atualizada para faixa {BELT_LABELS[new_color]}, {new_degree}º grau.', 'success')
        return redirect(url_for('gestao_graduacoes'))

    search_query = request.args.get('search', '').strip()
    belt_filter = request.args.get('belt', 'todas').strip().lower()
    role_filter = request.args.get('role', 'todos').strip().lower()
    users_query = User.query
    if search_query:
        pattern = f'%{search_query}%'
        users_query = users_query.filter(or_(User.name.ilike(pattern), User.username.ilike(pattern), User.cpf.ilike(pattern)))
    if belt_filter in BELT_COLORS:
        users_query = users_query.filter(User.belt_color == belt_filter)
    if role_filter in ROLE_LEVEL:
        users_query = users_query.filter(User.role == role_filter)
    users_list = users_query.order_by(User.name.asc()).all()
    all_users = User.query.all()
    belt_counts = {color: sum(1 for user in all_users if user.belt_color == color) for color in BELT_LABELS}
    recent_records = GraduationRecord.query.order_by(
        GraduationRecord.graduation_date.desc(), GraduationRecord.id.desc()).limit(12).all()
    return render_template(
        'gestao_graduacoes.html', page_title='Administração de Graduação', users=users_list,
        belt_labels=BELT_LABELS, belt_counts=belt_counts, total_users=len(all_users),
        recent_records=recent_records, search_query=search_query,
        belt_filter=belt_filter, role_filter=role_filter, today=datetime.now().date(),
    )

@app.route('/campeonatos/interno', methods=['GET', 'POST'])
@app.route('/campeonatos/interno.html', methods=['GET', 'POST'])
@login_required
def campeonato_interno():
    today = datetime.now().date()
    if request.method == 'POST':
        if session.get('user_role') not in {'monitor', 'instrutor'}:
            flash('Somente monitores e instrutores podem criar campeonatos.', 'error')
            return redirect(url_for('campeonato_interno'))
        name = request.form.get('name', '').strip()
        modality = request.form.get('modality', '').strip()
        location = request.form.get('location', '').strip()
        description = request.form.get('description', '').strip()
        max_participants = request.form.get('max_participants', type=int)
        try:
            event_date = datetime.strptime(request.form.get('event_date', ''), '%Y-%m-%d').date()
            registration_deadline = datetime.strptime(
                request.form.get('registration_deadline', ''), '%Y-%m-%d').date()
        except ValueError:
            event_date = registration_deadline = None
        allowed_modalities = {'Jiu-Jitsu', 'Boxe', 'Muay Thai', 'Multimodalidade'}
        if (not name or len(name) > 120 or modality not in allowed_modalities
                or not location or len(location) > 160 or len(description) > 500):
            flash('Revise nome, modalidade, local e descrição do campeonato.', 'error')
            return redirect(url_for('campeonato_interno'))
        if not event_date or not registration_deadline or event_date < today:
            flash('Informe datas válidas para o campeonato.', 'error')
            return redirect(url_for('campeonato_interno'))
        if registration_deadline < today or registration_deadline > event_date:
            flash('O prazo de inscrição deve ficar entre hoje e a data do campeonato.', 'error')
            return redirect(url_for('campeonato_interno'))
        if max_participants is None or not 2 <= max_participants <= 500:
            flash('O limite de participantes deve ficar entre 2 e 500.', 'error')
            return redirect(url_for('campeonato_interno'))
        championship = InternalChampionship(
            name=name, modality=modality, event_date=event_date,
            registration_deadline=registration_deadline, location=location,
            max_participants=max_participants, description=description or None,
            created_by_username=session.get('username', ''),
        )
        db.session.add(championship)
        db.session.commit()
        flash(f'Campeonato “{championship.name}” criado com sucesso!', 'success')
        return redirect(url_for('campeonato_interno'))

    championships = InternalChampionship.query.order_by(
        InternalChampionship.event_date.asc(), InternalChampionship.id.desc()).all()
    registered_ids = {registration.championship_id for registration in ChampionshipRegistration.query.filter_by(
        user_id=session['user_id'], status='inscrito').all()}
    return render_template(
        'campeonato_interno.html', page_title='Campeonatos • Interno',
        championships=championships, registered_ids=registered_ids, today=today,
    )

@app.route('/campeonatos/interno/<int:championship_id>', methods=['GET', 'POST'])
@login_required
def campeonato_interno_detalhe(championship_id):
    championship = db.get_or_404(InternalChampionship, championship_id)
    today = datetime.now().date()
    registration = ChampionshipRegistration.query.filter_by(
        championship_id=championship.id, user_id=session['user_id']).first()
    registration_open = (championship.status == 'inscricoes_abertas'
                         and championship.registration_deadline >= today
                         and championship.event_date >= today
                         and championship.registered_count < championship.max_participants)
    if request.method == 'POST':
        if registration and registration.status == 'inscrito':
            flash('Você já está inscrito neste campeonato.', 'warning')
            return redirect(url_for('campeonato_interno_detalhe', championship_id=championship.id))
        if not registration_open:
            flash('As inscrições deste campeonato não estão disponíveis.', 'error')
            return redirect(url_for('campeonato_interno_detalhe', championship_id=championship.id))
        weight = request.form.get('weight', type=float)
        age_division = request.form.get('age_division', '').strip()
        if weight is None or not 15 <= weight <= 250 or age_division not in {'Kids', 'Juvenil', 'Adulto', 'Master'}:
            flash('Informe peso e divisão válidos para concluir a inscrição.', 'error')
            return redirect(url_for('campeonato_interno_detalhe', championship_id=championship.id))
        current_user = db.session.get(User, session['user_id'])
        if registration:
            registration.weight, registration.age_division = weight, age_division
            registration.belt_color_snapshot, registration.status = current_user.belt_color, 'inscrito'
        else:
            registration = ChampionshipRegistration(
                championship_id=championship.id, user_id=current_user.id, weight=weight,
                age_division=age_division, belt_color_snapshot=current_user.belt_color,
            )
            db.session.add(registration)
        db.session.commit()
        flash(f'Inscrição confirmada no campeonato “{championship.name}”!', 'success')
        return redirect(url_for('campeonato_interno_detalhe', championship_id=championship.id))
    return render_template(
        'campeonato_interno_detalhe.html', page_title=championship.name,
        championship=championship, registration=registration,
        registration_open=registration_open, belt_labels=BELT_LABELS, today=today,
    )

@app.route('/campeonatos/pesos', methods=['GET', 'POST'])
@app.route('/campeonatos/pesos.html', methods=['GET', 'POST'])
@login_required
def campeonato_pesos():
    ensure_championship_weights()
    if request.method == 'POST':
        if session.get('user_role') not in {'monitor', 'instrutor'}:
            flash('Somente monitores e instrutores podem editar a tabela de pesos.', 'error')
            return redirect(url_for('campeonato_pesos'))
        division = db.session.get(ChampionshipWeightDivision, request.form.get('division_id', type=int))
        if not division:
            flash('Categoria de peso não encontrada.', 'error')
            return redirect(url_for('campeonato_pesos'))
        editable_fields = ['category'] + [column[0] for column in CHAMPIONSHIP_WEIGHT_COLUMNS]
        values = {field: request.form.get(field, '').strip() for field in editable_fields}
        if not values['category'] or any(len(value) > 40 for value in values.values()):
            flash('Revise a categoria e os limites informados.', 'error')
            return redirect(url_for('campeonato_pesos'))
        duplicate = ChampionshipWeightDivision.query.filter(
            ChampionshipWeightDivision.gender == division.gender,
            ChampionshipWeightDivision.category == values['category'],
            ChampionshipWeightDivision.id != division.id,
        ).first()
        if duplicate:
            flash('Já existe uma categoria com esse nome nesta tabela.', 'error')
            return redirect(url_for('campeonato_pesos'))
        changes = {}
        for field, new_value in values.items():
            old_value = getattr(division, field)
            if old_value != new_value:
                changes[field] = {'anterior': old_value, 'novo': new_value}
                setattr(division, field, new_value)
        if not changes:
            flash('Nenhuma alteração foi identificada nesta categoria.', 'warning')
            return redirect(url_for('campeonato_pesos'))
        division.updated_by_username = session.get('username', '')
        division.updated_at = datetime.utcnow()
        db.session.add(ChampionshipWeightRevision(
            division_id=division.id, changes_json=json.dumps(changes, ensure_ascii=False),
            updated_by_username=session.get('username', ''),
        ))
        db.session.commit()
        flash(f'Categoria {division.category} da tabela {division.gender} atualizada.', 'success')
        return redirect(url_for('campeonato_pesos'))
    tables = {
        gender: ChampionshipWeightDivision.query.filter_by(gender=gender).order_by(
            ChampionshipWeightDivision.sort_order).all()
        for gender in ('masculino', 'feminino')
    }
    last_revision = ChampionshipWeightRevision.query.order_by(
        ChampionshipWeightRevision.created_at.desc()).first()
    return render_template(
        'campeonato_pesos.html', page_title='Campeonatos • Tabela de Pesos',
        weight_columns=CHAMPIONSHIP_WEIGHT_COLUMNS, weight_tables=tables,
        last_revision=last_revision,
    )

@app.route('/campeonatos/placar', methods=['GET', 'POST'])
@app.route('/campeonatos/placar.html', methods=['GET', 'POST'])
@app.route('/campeonatos/placar-e-timer', methods=['GET', 'POST'])
@app.route('/campeonatos/placar-e-timer.html', methods=['GET', 'POST'])
@login_required
def campeonato_placar():
    can_control = session.get('user_role') in {'monitor', 'instrutor'}
    if request.method == 'POST':
        if not can_control:
            flash('Somente monitores e instrutores podem controlar o placar.', 'error')
            return redirect(url_for('campeonato_placar'))
        action = request.form.get('action', '')
        requested_view = request.form.get('scoreboard_view', 'placar')
        requested_view = requested_view if requested_view in {'placar', 'timer'} else 'placar'
        if action == 'create_match':
            championship_id = request.form.get('championship_id', type=int)
            championship = db.session.get(InternalChampionship, championship_id) if championship_id else None
            if not championship:
                championship = InternalChampionship.query.first()
                if not championship:
                    championship = InternalChampionship(
                        name="Torneio Interno BJ Sports 2026",
                        event_date=datetime.now(),
                        location="Centro de Treinamento BJ Sports",
                        status="em_andamento"
                    )
                    db.session.add(championship)
                    db.session.flush()

            red_name = request.form.get('red_competitor', '').strip()
            blue_name = request.form.get('blue_competitor', '').strip()
            category = request.form.get('category', '').strip()
            mat_area = request.form.get('mat_area', '').strip() or 'Área 1'
            duration_minutes = request.form.get('duration_minutes', type=int) or 5
            penalty_limit = request.form.get('penalty_limit', type=int) or 4
            if (not red_name or not blue_name or red_name.casefold() == blue_name.casefold()
                    or len(red_name) > 120 or len(blue_name) > 120 or not category
                    or len(category) > 120 or not mat_area or len(mat_area) > 40
                    or duration_minutes not in CHAMPIONSHIP_MATCH_DURATIONS or penalty_limit not in {4, 6}):
                flash('Revise atletas, categoria, área e duração da luta.', 'error')
                return redirect(url_for('campeonato_placar'))
            match = ChampionshipMatch(
                championship_id=championship.id, red_competitor=red_name,
                blue_competitor=blue_name, category=category, mat_area=mat_area,
                duration_seconds=duration_minutes * 60, remaining_seconds=duration_minutes * 60,
                penalty_limit=penalty_limit,
                updated_by_username=session.get('username', ''),
            )
            db.session.add(match)
            db.session.commit()
            flash('Novo confronto/área criado e pronto para o placar.', 'success')
            return redirect(url_for('campeonato_placar', match=match.id))

        match = db.session.get(ChampionshipMatch, request.form.get('match_id', type=int))
        if not match:
            flash('Confronto não encontrado.', 'error')
            return redirect(url_for('campeonato_placar'))

        if action == 'delete_match':
            db.session.delete(match)
            db.session.commit()
            flash('Confronto/Área removido com sucesso.', 'success')
            return redirect(url_for('campeonato_placar'))
        was_running = match.timer_running
        remaining = match_remaining_seconds(match)
        match.remaining_seconds = remaining
        match.timer_started_at = None
        score_actions = {
            'mount_back': ('Montada ou costas', 4),
            'guard_pass': ('Passagem de guarda', 3),
            'two_points': ('Queda, raspagem ou joelho na barriga', 2),
            'advantage': ('Vantagem', 0),
            'penalty': ('Punição', 0),
        }
        duration_actions = {
            f'set_duration_{minutes}': minutes * 60
            for minutes in CHAMPIONSHIP_MATCH_DURATIONS
        }
        if action in duration_actions and match.status != 'finalizada':
            match.duration_seconds = duration_actions[action]
            match.remaining_seconds = duration_actions[action]
            match.timer_running, match.timer_started_at, match.status = False, None, 'aguardando'
        elif action == 'set_custom_duration' and match.status != 'finalizada':
            custom_minutes = request.form.get('custom_minutes', type=int)
            custom_seconds = request.form.get('custom_seconds', type=int)
            if (custom_minutes is None or custom_seconds is None or not 0 <= custom_minutes <= 99
                    or not 0 <= custom_seconds <= 59 or custom_minutes * 60 + custom_seconds < 1):
                flash('Informe um tempo válido entre 00:01 e 99:59.', 'error')
                return redirect(url_for('campeonato_placar', match=match.id, view='timer'))
            custom_duration = custom_minutes * 60 + custom_seconds
            match.duration_seconds = custom_duration
            match.remaining_seconds = custom_duration
            match.timer_running, match.timer_started_at, match.status = False, None, 'aguardando'
        elif action == 'start_timer' and remaining > 0 and match.status != 'finalizada':
            match.timer_running, match.timer_started_at, match.status = True, datetime.utcnow(), 'em_andamento'
        elif action == 'pause_timer' and match.status != 'finalizada':
            match.timer_running, match.status = False, 'pausada'
        elif action == 'reset_timer' and match.status != 'finalizada':
            match.timer_running, match.remaining_seconds, match.status = False, match.duration_seconds, 'aguardando'
        elif action == 'undo_score_event':
            event = ChampionshipScoreEvent.query.filter_by(match_id=match.id, undone_at=None).order_by(
                ChampionshipScoreEvent.id.desc()
            ).first()
            if not event:
                flash('Não há lançamento para desfazer.', 'info')
                return redirect(url_for('campeonato_placar', match=match.id, view='placar'))
            before = json.loads(event.before_state_json)
            for field in ('red_score', 'blue_score', 'red_advantages', 'blue_advantages',
                          'red_penalties', 'blue_penalties', 'status', 'winner_side'):
                setattr(match, field, before[field])
            match.timer_running, match.timer_started_at = False, None
            event.undone_at = datetime.utcnow()
            event.undone_by_username = session.get('username', '')
            flash(f'Lançamento desfeito: {event.label}.', 'success')
        elif action in {'red_disqualify', 'blue_disqualify'} and match.status != 'finalizada':
            side = action.split('_', 1)[0]
            opponent = 'blue' if side == 'red' else 'red'
            before = {
                field: getattr(match, field) for field in (
                    'red_score', 'blue_score', 'red_advantages', 'blue_advantages',
                    'red_penalties', 'blue_penalties', 'status', 'winner_side'
                )
            }
            match.timer_running, match.timer_started_at = False, None
            match.status, match.winner_side = 'finalizada', opponent
            db.session.add(ChampionshipScoreEvent(
                match_id=match.id, side=side, action_key='disqualification',
                label='Desclassificação direta', consequence='Adversário declarado vencedor',
                before_state_json=json.dumps(before),
                created_by_username=session.get('username', ''),
            ))
        elif '_' in action and action.split('_', 1)[0] in {'red', 'blue'} and action.split('_', 1)[1] in score_actions and match.status != 'finalizada':
            side, action_key = action.split('_', 1)
            label, points = score_actions[action_key]
            opponent = 'blue' if side == 'red' else 'red'
            before = {
                field: getattr(match, field) for field in (
                    'red_score', 'blue_score', 'red_advantages', 'blue_advantages',
                    'red_penalties', 'blue_penalties', 'status', 'winner_side'
                )
            }
            consequence = None
            if points:
                setattr(match, f'{side}_score', getattr(match, f'{side}_score') + points)
                consequence = f'+{points} pontos'
            elif action_key == 'advantage':
                setattr(match, f'{side}_advantages', getattr(match, f'{side}_advantages') + 1)
                consequence = '+1 vantagem'
            else:
                penalties = getattr(match, f'{side}_penalties') + 1
                setattr(match, f'{side}_penalties', penalties)
                consequence = f'{penalties}ª punição registrada'
                penalty_limit = match.penalty_limit or 4
                if penalties == 2:
                    setattr(match, f'{opponent}_advantages', getattr(match, f'{opponent}_advantages') + 1)
                    consequence += '; vantagem automática para o adversário'
                elif penalties == 3 or (penalty_limit == 6 and penalties in {4, 5}):
                    setattr(match, f'{opponent}_score', getattr(match, f'{opponent}_score') + 2)
                    consequence += '; 2 pontos automáticos para o adversário'
                elif penalties >= penalty_limit:
                    match.timer_running, match.status, match.winner_side = False, 'finalizada', opponent
                    consequence += '; desclassificação'
            db.session.add(ChampionshipScoreEvent(
                match_id=match.id, side=side, action_key=action_key, label=label,
                consequence=consequence, before_state_json=json.dumps(before),
                created_by_username=session.get('username', ''),
            ))
            if was_running and remaining > 0 and match.status != 'finalizada':
                match.timer_running, match.timer_started_at = True, datetime.utcnow()
        elif action == 'finish_match':
            match.timer_running, match.status = False, 'finalizada'
            red_key = (match.red_score, match.red_advantages, -match.red_penalties)
            blue_key = (match.blue_score, match.blue_advantages, -match.blue_penalties)
            match.winner_side = 'red' if red_key > blue_key else ('blue' if blue_key > red_key else 'draw')
        elif action == 'reopen_match':
            match.timer_running, match.status, match.winner_side = False, 'pausada', None
        else:
            flash('Ação de placar inválida para o estado atual da luta.', 'error')
            return redirect(url_for('campeonato_placar', match=match.id, view=requested_view))
        match.updated_by_username = session.get('username', '')
        db.session.commit()
        return redirect(url_for('campeonato_placar', match=match.id, view=requested_view))

    matches = ChampionshipMatch.query.order_by(ChampionshipMatch.id.desc()).all()
    selected_id = request.args.get('match', type=int)
    selected_match = next((item for item in matches if item.id == selected_id), None) if selected_id else None
    selected_match = selected_match or (matches[0] if matches else None)
    remaining_seconds = match_remaining_seconds(selected_match) if selected_match else 0
    scoreboard_view = 'timer' if request.args.get('view') == 'timer' else 'placar'
    championships = InternalChampionship.query.order_by(InternalChampionship.event_date.desc()).all()
    recent_score_events = ChampionshipScoreEvent.query.filter_by(
        match_id=selected_match.id, undone_at=None
    ).order_by(ChampionshipScoreEvent.id.desc()).limit(8).all() if selected_match else []
    return render_template(
        'campeonato_placar.html', page_title='Campeonatos • Placar e Timer', matches=matches,
        selected_match=selected_match, remaining_seconds=remaining_seconds,
        championships=championships, can_control=can_control, scoreboard_view=scoreboard_view,
        recent_score_events=recent_score_events,
    )

@app.route('/integracoes/pagamentos')
@app.route('/integracoes/pagamentos.html')
@role_required('instrutor')
def integracoes_pagamentos():
    provider_configured = bool(os.getenv('PAYMENT_PROVIDER') and os.getenv('PAYMENT_API_KEY'))
    webhook_configured = bool(os.getenv('PAYMENT_WEBHOOK_SECRET'))
    return render_template(
        'integracoes_pagamentos.html',
        page_title='Integrações • Pagamentos',
        provider_configured=provider_configured,
        webhook_configured=webhook_configured,
    )

@app.route('/integracoes/catraca')
@app.route('/integracoes/catraca.html')
@role_required('instrutor')
def integracoes_catraca():
    device_configured = bool(os.getenv('TURNSTILE_API_URL') and os.getenv('TURNSTILE_API_KEY'))
    device_model = os.getenv('TURNSTILE_DEVICE_MODEL', 'Fit Easy')
    device_brand = os.getenv('TURNSTILE_DEVICE_BRAND', 'Topdata')
    device_identified = bool(device_model and device_brand)
    return render_template(
        'integracoes_catraca.html', page_title='Integrações • Catraca',
        device_configured=device_configured, device_identified=device_identified,
        device_model=device_model, device_brand=device_brand,
    )

def get_sponsored_plan_type_for_user(user):
    if not user or user.sponsor_id:
        return None
    plan_lower = (user.plan or '').lower()
    if any(k in plan_lower for k in ['casal', 'duo', 'parceir']):
        return 'couple'
    if any(k in plan_lower for k in ['família', 'familia', 'membro', 'dependente', 'grupo', 'parentes']):
        return 'family'
    if user.sponsored_dependents or user.role in {'instrutor', 'professor', 'admin'}:
        return 'family'
    return None

@app.route('/configuracoes', methods=['GET', 'POST'])
@app.route('/configuracoes.html', methods=['GET', 'POST'])
@login_required
def configuracoes():
    user = db.session.get(User, session['user_id'])
    sponsored_plan_type = get_sponsored_plan_type_for_user(user)

    if request.method == 'POST':
        action = request.form.get('action', 'update_profile')
        if action == 'save_family_combo':
            titular_modality = request.form.get('titular_modality', '').strip()
            if titular_modality:
                user.selected_modalities = titular_modality

            existing_dependents = {d.id: d for d in user.sponsored_dependents}
            submitted_ids = set()

            # Processar integrantes enviados
            member_indices = [k.replace('family_member_id_', '') for k in request.form.keys() if k.startswith('family_member_id_')]
            
            valid_new_dependents = []
            for idx in member_indices:
                dep_id = request.form.get(f'family_member_id_{idx}', type=int)
                dep_mod = request.form.get(f'family_member_modality_{idx}', '').strip()
                if dep_id and dep_id != user.id:
                    dep_user = db.session.get(User, dep_id)
                    if dep_user and (dep_user.sponsor_id is None or dep_user.sponsor_id == user.id):
                        submitted_ids.add(dep_user.id)
                        dep_user.sponsor_id = user.id
                        dep_user.sponsor_started_at = dep_user.sponsor_started_at or datetime.utcnow()
                        dep_user.plan = user.plan
                        if dep_mod:
                            dep_user.selected_modalities = dep_mod
                        valid_new_dependents.append(dep_user)

            # Desvincular integrantes removidos
            for old_id, old_dep in existing_dependents.items():
                if old_id not in submitted_ids:
                    old_dep.sponsor_id = None
                    old_dep.sponsor_started_at = None
                    if old_dep.sponsored_previous_plan:
                        old_dep.plan = old_dep.sponsored_previous_plan
                    old_dep.sponsored_previous_modalities = None
                    old_dep.sponsored_previous_plan = None

            total_members = 1 + len(submitted_ids)
            extra_members = max(0, total_members - 3)
            base_price = Decimal('280.00')
            extra_price = Decimal('70.00') * extra_members
            total_combo_price = base_price + extra_price

            user.plan = f"Plano Família ({total_members} Integrantes) — R$ {total_combo_price:.2f}/mês".replace('.', ',')

            # Atualiza o valor da fatura do mês atual se estiver em aberto
            now = datetime.now()
            open_payment = MonthlyPayment.query.filter_by(user_id=user.id, year=now.year, month=now.month, status='atrasado').first()
            if not open_payment:
                open_payment = MonthlyPayment.query.filter_by(user_id=user.id, year=now.year, month=now.month, status='futuro').first()
            if open_payment:
                open_payment.amount = total_combo_price

            db.session.commit()
            flash(f'✨ Combo Família salvo com sucesso! {total_members} integrantes vinculados. Fatura do grupo: R$ {total_combo_price:.2f}/mês'.replace('.', ','), 'success')
            return redirect(url_for('configuracoes'))
            dependent_user_id = request.form.get('dependent_user_id', type=int)
            search_query = request.form.get('dependent_search', '').strip() or request.form.get('dependent_cpf3', '').strip()
            
            target_dependent = None
            if dependent_user_id:
                target_dependent = db.session.get(User, dependent_user_id)
            elif search_query:
                clean_digits = ''.join(c for c in search_query if c.isdigit())
                query_filter = User.query.filter(User.id != user.id)
                if clean_digits and len(clean_digits) >= 3:
                    candidates = [c for c in query_filter.all() if ''.join(ch for ch in c.cpf if ch.isdigit()).startswith(clean_digits)]
                else:
                    candidates = query_filter.filter(
                        User.name.ilike(f'%{search_query}%') | User.username.ilike(f'%{search_query}%')
                    ).all()

                if not candidates:
                    flash('Nenhum cadastro válido foi encontrado com esses dados.', 'error')
                elif len(candidates) > 1:
                    flash('Mais de um cadastro foi encontrado. Selecione a pessoa específica na lista suspensa.', 'error')
                else:
                    target_dependent = candidates[0]

            if target_dependent:
                if target_dependent.id == user.id:
                    flash('Você não pode adicionar a si mesmo como dependente.', 'error')
                elif target_dependent.sponsor_id:
                    flash(f'{target_dependent.name} já está vinculado(a) ao plano de outro titular.', 'error')
                elif target_dependent.sponsored_dependents:
                    flash('Uma conta que já possui dependentes não pode ser adicionada como dependente.', 'error')
                else:
                    target_dependent.sponsored_previous_plan = target_dependent.plan
                    target_dependent.sponsored_previous_modalities = target_dependent.selected_modalities
                    target_dependent.sponsor_id = user.id
                    target_dependent.sponsor_started_at = datetime.utcnow()
                    target_dependent.plan = user.plan
                    target_dependent.selected_modalities = user.selected_modalities
                    db.session.commit()
                    flash(f'✨ {target_dependent.name} foi incluído(a) com sucesso no seu plano {user.plan}!', 'success')
            return redirect(url_for('configuracoes'))
        if action == 'remove_plan_dependent':
            dependent = db.session.get(User, request.form.get('dependent_id', type=int))
            if not dependent or dependent.sponsor_id != user.id:
                flash('Integrante não encontrado neste plano.', 'error')
            else:
                dependent.sponsor_id = None
                dependent.sponsor_started_at = None
                if dependent.sponsored_previous_plan:
                    dependent.plan = dependent.sponsored_previous_plan
                dependent.selected_modalities = dependent.sponsored_previous_modalities
                dependent.sponsored_previous_plan = None
                dependent.sponsored_previous_modalities = None
                db.session.commit()
                flash(f'{dependent.name} foi removido(a) do plano compartilhado.', 'info')
            return redirect(url_for('configuracoes'))
        new_name = request.form.get('name', '').strip()
        new_phone = request.form.get('phone', '').strip()
        new_belt_color = request.form.get('belt_color', '').strip().lower()
        new_belt_degree = request.form.get('belt_degree', type=int)
        new_medical_restriction = request.form.get('medical_restriction', '').strip()
        phone_digits = ''.join(c for c in new_phone if c.isdigit())
        if new_name and len(phone_digits) in {11, 13}:
            local = phone_digits[-11:]
            user.name, user.ddd, user.phone = new_name, local[:2], local[2:]
            if new_belt_color in BELT_COLORS:
                user.belt_color = new_belt_color
            if new_belt_degree is not None and 0 <= new_belt_degree <= 4:
                user.belt_degree = new_belt_degree
            user.medical_restriction = new_medical_restriction if new_medical_restriction else None
            db.session.commit()
            session['user_name'] = new_name
            flash('Configurações e informações do perfil salvas com sucesso!', 'success')
        else:
            flash('Nome ou telefone inválido.', 'error')
        return redirect(url_for('configuracoes'))

    available_students = User.query.filter(User.id != user.id, User.sponsor_id.is_(None)).order_by(User.name).all()
    return render_template('configuracoes.html', page_title='Configurações & Perfil', profile_user=user,
                           sponsored_plan_type=sponsored_plan_type, available_students=available_students)

@app.route('/gestao/modalidades-combo', methods=['GET', 'POST'])
@login_required
def gestao_modalidades_combo():
    if session.get('user_role') not in {'professor', 'instrutor', 'monitor'}:
        flash('Somente professores e monitores podem alterar modalidades de combos.', 'error')
        return redirect(url_for('dashboard'))

    allowed_modalities = {'Jiu-Jitsu', 'Boxe', 'Muay Thai', 'MMA'}
    selectable_plans = [plan for plan in Plan.query.all() if plan.get_selection_count()]

    def selectable_plan_for(student):
        if not student:
            return None
        return next((plan for plan in selectable_plans if student.plan.startswith(plan.name)), None)

    if request.method == 'POST':
        student = db.session.get(User, request.form.get('user_id', type=int))
        selected = [value.strip() for value in request.form.getlist('combo_modalities') if value.strip()]
        student_plan = selectable_plan_for(student)
        expected_count = student_plan.get_selection_count() if student_plan else 0
        if not student or not expected_count:
            flash('Aluno ou plano combo inválido.', 'error')
        elif len(selected) != expected_count or len(set(selected)) != expected_count:
            flash(f'Escolha exatamente {expected_count} modalidades diferentes.', 'error')
        elif any(modality not in allowed_modalities or modality not in student_plan.get_modalities() for modality in selected):
            flash('Uma das modalidades informadas é inválida.', 'error')
        else:
            student.selected_modalities = ', '.join(selected)
            db.session.commit()
            flash(f'Modalidades do combo de {student.name} atualizadas.', 'success')
        return redirect(url_for('gestao_modalidades_combo'))

    combo_students = [student for student in User.query.filter_by(role='aluno').order_by(User.name.asc()).all()
                      if selectable_plan_for(student)]
    combo_counts = {student.id: selectable_plan_for(student).get_selection_count() for student in combo_students}
    combo_options = {student.id: selectable_plan_for(student).get_modalities() for student in combo_students}
    return render_template('gestao_modalidades_combo.html', page_title='Modalidades dos Combos',
                           combo_students=combo_students,
                           combo_counts=combo_counts, combo_options=combo_options)

@app.route('/minha-conta/contrato', methods=['GET', 'POST'])
@app.route('/minha-conta/contrato.html', methods=['GET', 'POST'])
@login_required
def contrato():
    user = db.session.get(User, session['user_id'])
    authorized_image_scopes = {'adult', 'minor_guardian'}
    image_authorization_required = user.image_consent_scope not in authorized_image_scopes
    is_pending = (
        user.membership_terms_version != MEMBERSHIP_TERMS_VERSION
        or user.privacy_notice_version != PRIVACY_NOTICE_VERSION
        or image_authorization_required
    )

    if request.method == 'POST':
        submitted_image_scope = request.form.get('imageConsentScope', '').strip()
        effective_image_scope = (
            user.image_consent_scope
            if user.image_consent_scope in authorized_image_scopes
            else submitted_image_scope
        )
        guardian_name = request.form.get('imageGuardianName', '').strip()
        guardian_cpf = request.form.get('imageGuardianCpf', '').strip()
        guardian_relationship = request.form.get('imageGuardianRelationship', '').strip()
        image_errors = []
        if effective_image_scope not in authorized_image_scopes:
            image_errors.append('Autorize o uso de imagem para aceitar esta versão do contrato.')
        elif effective_image_scope == 'minor_guardian' and image_authorization_required:
            guardian_cpf_digits = ''.join(character for character in guardian_cpf if character.isdigit())
            if len(guardian_name) < 3:
                image_errors.append('Informe o nome completo do responsável pela autorização de imagem do menor.')
            if not is_valid_cpf(guardian_cpf_digits):
                image_errors.append('Informe um CPF válido para o responsável pela autorização de imagem.')
            if guardian_relationship not in {'mae', 'pai', 'responsavel_legal'}:
                image_errors.append('Informe o vínculo do responsável legal pelo menor.')
        if request.form.get('action') != 'accept_contract_update':
            flash('Ação de contrato inválida.', 'error')
        elif not is_pending:
            flash('Seu contrato já está atualizado.', 'info')
        elif request.form.get('acceptContractUpdate') != 'on':
            flash('Leia o contrato e marque a confirmação para registrar o aceite.', 'error')
        elif image_errors:
            for error in image_errors:
                flash(error, 'error')
        else:
            accepted_at = datetime.utcnow()
            user.membership_terms_version = MEMBERSHIP_TERMS_VERSION
            user.membership_terms_accepted_at = accepted_at
            user.privacy_notice_version = PRIVACY_NOTICE_VERSION
            user.privacy_notice_accepted_at = accepted_at
            if image_authorization_required:
                user.image_use_consent = True
                user.image_use_consent_at = accepted_at
                user.image_consent_scope = effective_image_scope
                user.image_consent_guardian_name = guardian_name if effective_image_scope == 'minor_guardian' else None
                user.image_consent_guardian_cpf = guardian_cpf if effective_image_scope == 'minor_guardian' else None
                user.image_consent_guardian_relationship = guardian_relationship if effective_image_scope == 'minor_guardian' else None
            db.session.add(ContractAcceptance(
                user_id=user.id,
                membership_terms_version=MEMBERSHIP_TERMS_VERSION,
                privacy_notice_version=PRIVACY_NOTICE_VERSION,
                image_consent_scope=effective_image_scope,
                source='account_update',
                accepted_at=accepted_at,
            ))
            db.session.commit()
            flash('Atualização do contrato aceita e registrada com sucesso.', 'success')
        return redirect(url_for('contrato'))

    consent_labels = {
        'none': 'Uso de imagem não autorizado',
        'adult': 'Autorizado pelo aluno adulto',
        'minor_guardian': 'Autorizado pelo responsável legal',
    }
    history = ContractAcceptance.query.filter_by(user_id=user.id).order_by(
        ContractAcceptance.accepted_at.desc(), ContractAcceptance.id.desc()
    ).all()
    return render_template(
        'contrato.html', page_title='Minha Conta • Contrato', contract_user=user,
        contract_pending=is_pending, current_terms_version=MEMBERSHIP_TERMS_VERSION,
        current_privacy_version=PRIVACY_NOTICE_VERSION,
        contract_plan_text=user.plan, contract_due_text=f'dia {user.due_date} de cada mês',
        image_consent_label=consent_labels.get(user.image_consent_scope, consent_labels['none']),
        image_authorization_required=image_authorization_required,
        acceptance_history=history,
    )

@app.route('/aluno')
@app.route('/aluno.html')
def aluno_portal():
    return redirect(url_for('login'))

@app.route('/alterar-senha-temporaria', methods=['GET', 'POST'])
@login_required
def change_temporary_password():
    user = db.session.get(User, session['user_id'])
    if not user.must_change_password:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        password = request.form.get('new_password', '')
        confirmation = request.form.get('confirm_password', '')
        if password != confirmation:
            flash('As senhas não coincidem.', 'error')
        elif (len(password) < 8 or not re.search(r'\d', password)
              or not re.search(r'[A-Z]', password) or not re.search(r'[a-z]', password)):
            flash('A nova senha deve ter pelo menos 8 caracteres, com número, letra maiúscula e letra minúscula.', 'error')
        else:
            user.set_password(password)
            user.must_change_password = False
            db.session.commit()
            flash('Senha alterada com sucesso. Seu acesso foi liberado.', 'success')
            return redirect(url_for('dashboard'))
    return render_template('alterar_senha_temporaria.html', page_title='Criar nova senha')

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    if request.method == 'GET':
        return render_template('logout.html', page_title='Sair da Conta')
    session.clear()
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('login', logout='1'))

if __name__ == '__main__':
    app.run(host=os.getenv('HOST', '127.0.0.1'), port=int(os.getenv('PORT', '5050')),
            debug=os.getenv('FLASK_DEBUG') == '1')
