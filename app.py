import os
import json
import re
import urllib.parse
import secrets
import click
import tempfile
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text, or_
from itsdangerous import URLSafeSerializer, BadSignature
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from store_catalog import STORE_PRODUCTS
from financial_reports import build_financial_markdown, markdown_to_pdf, financial_report_to_xlsx

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'bjsports-production-secret-key-2026-cajazeiras')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///bjsports.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = os.getenv('SESSION_COOKIE_SECURE', '0') == '1'

if os.getenv('FLASK_ENV') == 'production' and not os.getenv('SECRET_KEY'):
    raise RuntimeError('SECRET_KEY é obrigatória em produção.')

db = SQLAlchemy(app)
calendar_token_serializer = URLSafeSerializer(app.config['SECRET_KEY'], salt='personal-calendar-feed')

ROLE_LEVEL = {'aluno': 0, 'monitor': 1, 'instrutor': 2}
MEMBERSHIP_TERMS_VERSION = '2026-08-17.4'
PRIVACY_NOTICE_VERSION = '2026-08-17'
BELT_COLORS = {'branca', 'azul', 'roxa', 'marrom', 'preta'}
BELT_LABELS = {'branca': 'Branca', 'azul': 'Azul', 'roxa': 'Roxa', 'marrom': 'Marrom', 'preta': 'Preta'}
CLASS_MANAGEMENT_PREVIEW = [
    {'id': 1, 'name': 'Jiu-Jitsu Kids 1', 'modality': 'Jiu-Jitsu', 'audience': 'Kids',
     'schedules': ['Ter, Qui • 17:00'], 'weekly_sessions': 2, 'instructor': 'Mestre Bolivar',
     'capacity': 16, 'enrolled': 14, 'waiting': 0, 'status': 'ativa'},
    {'id': 2, 'name': 'Jiu-Jitsu Kids 2', 'modality': 'Jiu-Jitsu', 'audience': 'Kids',
     'schedules': ['Seg, Qua • 16:00'], 'weekly_sessions': 2, 'instructor': 'Mestre Bolivar',
     'capacity': 16, 'enrolled': 12, 'waiting': 0, 'status': 'ativa'},
    {'id': 3, 'name': 'Jiu-Jitsu Almoço', 'modality': 'Jiu-Jitsu', 'audience': 'Adulto',
     'schedules': ['Ter, Qui • 12:00'], 'weekly_sessions': 2, 'instructor': 'Mestre Bolivar',
     'capacity': 20, 'enrolled': 8, 'waiting': 0, 'status': 'ativa'},
    {'id': 4, 'name': 'Jiu-Jitsu Tarde', 'modality': 'Jiu-Jitsu', 'audience': 'Adulto',
     'schedules': ['Seg, Qua, Sex • 17:00'], 'weekly_sessions': 3, 'instructor': 'Mestre Bolivar',
     'capacity': 20, 'enrolled': 18, 'waiting': 0, 'status': 'ativa'},
    {'id': 5, 'name': 'Jiu-Jitsu Noturno', 'modality': 'Jiu-Jitsu', 'audience': 'Adulto',
     'schedules': ['Seg, Qua, Sex • 19:00', 'Ter, Qui • 19:00'], 'weekly_sessions': 5,
     'instructor': 'Mestre Bolivar', 'capacity': 20, 'enrolled': 20, 'waiting': 3, 'status': 'lotada'},
    {'id': 6, 'name': 'Boxe Matinal', 'modality': 'Boxe', 'audience': 'Adulto',
     'schedules': ['Seg, Qua, Sex • 06:00'], 'weekly_sessions': 3, 'instructor': 'Mestre Bolivar',
     'capacity': 20, 'enrolled': 11, 'waiting': 0, 'status': 'ativa'},
    {'id': 7, 'name': 'Boxe Noturno', 'modality': 'Boxe', 'audience': 'Adulto',
     'schedules': ['Ter, Qui • 19:00'], 'weekly_sessions': 2, 'instructor': 'Mestre Bolivar',
     'capacity': 20, 'enrolled': 9, 'waiting': 0, 'status': 'ativa'},
    {'id': 8, 'name': 'Muay Thai Kids', 'modality': 'Muay Thai', 'audience': 'Kids',
     'schedules': ['Ter, Qui • 18:00'], 'weekly_sessions': 2, 'instructor': 'Mestre Bolivar',
     'capacity': 16, 'enrolled': 13, 'waiting': 0, 'status': 'ativa'},
    {'id': 9, 'name': 'Muay Thai', 'modality': 'Muay Thai', 'audience': 'Adulto',
     'schedules': ['Seg, Qua, Sex • 07:30 e 18:00', 'Ter, Qui • 20:00'], 'weekly_sessions': 8,
     'instructor': 'Mestre Bolivar', 'capacity': 20, 'enrolled': 17, 'waiting': 0, 'status': 'ativa'},
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
        if not supplied or not secrets.compare_digest(supplied, session.get('_csrf_token', '')):
            return jsonify({'error': 'Token CSRF inválido ou ausente.'}), 400

@app.after_request
def add_security_headers(response):
    response.headers.setdefault('X-Content-Type-Options', 'nosniff')
    response.headers.setdefault('X-Frame-Options', 'SAMEORIGIN')
    response.headers.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_overdue_payments(self):
        return self.get_overdue_details()['count'] > 0

    def is_fee_exempt_for(self, year=None, month=None):
        today = datetime.now()
        year, month = year or today.year, month or today.month
        period_key = year * 100 + month
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
        persisted = {p.month: p.status for p in self.payments if p.year == year}

        for m in range(start, 13):
            m_str = f"{m:02d}"
            if m in persisted and persisted[m] == 'pago':
                status = 'pago'
            elif self.is_fee_exempt_for(year, m):
                status = 'isento'
            elif m in persisted:
                status = persisted[m]
            elif m_str in hist:
                status = hist[m_str]
            else:
                if m < current_month:
                    status = 'pago' # Verde
                elif m == current_month:
                    if self.payment_status == 'Em Dia':
                        status = 'pago' # Verde
                    else:
                        status = 'atrasado' # Laranja
                else:
                    status = 'futuro' # Branco

            months.append({
                'month': m_str,
                'name': month_names.get(m, ''),
                'status': status
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
                return float(val_str)
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
    sub = db.Column(db.String(200), nullable=True)
    features = db.Column(db.Text, nullable=True)
    is_featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login_or_name = db.Column(db.String(120), nullable=False)
    cpf3 = db.Column(db.String(3), nullable=True)
    modality = db.Column(db.String(100), nullable=False)
    shift_time = db.Column(db.String(150), nullable=False)
    is_experimental = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
    capacity = db.Column(db.Integer, nullable=False, default=20)
    waiting = db.Column(db.Integer, nullable=False, default=0)
    duration_minutes = db.Column(db.Integer, nullable=False, default=60)
    status = db.Column(db.String(20), nullable=False, default='ativa')
    publish_public = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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

def ensure_class_groups():
    if ClassGroup.query.count() == 0:
        for item in CLASS_MANAGEMENT_PREVIEW:
            class_group = ClassGroup(
                name=item['name'], modality=item['modality'], audience=item['audience'],
                instructor=item['instructor'], capacity=item['capacity'], waiting=item['waiting'],
                duration_minutes=60, status=item['status'], publish_public=True,
            )
            class_group.schedules = item['schedules']
            db.session.add(class_group)
        db.session.commit()

    if ClassEnrollment.query.count() == 0:
        adult_groups = ClassGroup.query.filter_by(audience='Adulto').order_by(ClassGroup.id).all()
        jiu_groups = [group for group in adult_groups if group.modality == 'Jiu-Jitsu']
        boxe_groups = [group for group in adult_groups if group.modality == 'Boxe']
        for index, user in enumerate(User.query.filter_by(role='aluno').order_by(User.id).all()):
            normalized_plan = user.plan.casefold()
            if 'jiu-jitsu' in normalized_plan or 'bjj' in normalized_plan:
                candidates = jiu_groups
            elif 'boxe tradicional' in normalized_plan:
                candidates = boxe_groups
            else:
                candidates = adult_groups
            if candidates:
                db.session.add(ClassEnrollment(
                    user_id=user.id, class_group_id=candidates[index % len(candidates)].id,
                    active=True, is_demo=True,
                ))
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

with app.app_context():
    try:
        db.create_all()
    except Exception:
        db.session.rollback()

    # Migração compatível com a base SQLite já existente.
    user_columns = {column['name'] for column in inspect(db.engine).get_columns('user')}
    if 'belt_color' not in user_columns:
        db.session.execute(text('ALTER TABLE "user" ADD COLUMN belt_color VARCHAR(20) NOT NULL DEFAULT \'branca\''))
    if 'belt_degree' not in user_columns:
        db.session.execute(text('ALTER TABLE "user" ADD COLUMN belt_degree INTEGER NOT NULL DEFAULT 0'))
    if 'monthly_fee_exempt' not in user_columns:
        db.session.execute(text('ALTER TABLE "user" ADD COLUMN monthly_fee_exempt BOOLEAN NOT NULL DEFAULT 0'))
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
    db.session.commit()

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
    
    if not Plan.query.first():
        p1 = Plan(name='⚡ Plano Passe Livre', category='Planos Individuais', price='R$ 120,00/mês', sub='Acesso total a todas as modalidades e horários', features='Liberdade de treinar todos os dias;Acesso aos treinos da manhã, tarde e noite;Acompanhamento individual de evolução', is_featured=True)
        p2 = Plan(name='🔥 Plano Casal', category='Planos Promocionais & Família', price='R$ 190,00/mês', sub='Para 2 pessoas treinando juntas', features='Válido para qualquer modalidade;Matrícula conjunta simplificada;Incentivo mútuo nos treinos', is_featured=False)
        p3 = Plan(name='Plano Família', category='Planos Promocionais & Família', price='R$ 280,00/mês', sub='Pacote especial para 3 familiares', features='Válido para 3 membros da família;Inclui Jiu-Jitsu Kids e Adulto;Maior economia por aluno', is_featured=False)
        p4 = Plan(name='Jiu-Jitsu (Seg, Qua, Sex)', category='Planos Individuais', price='R$ 100,00/mês', sub='Treinos 3x por semana', features='Treinos de fundamentos e ralas;Turmas da tarde e noite', is_featured=False)
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

    ensure_class_groups()


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
    pending_attendance_count = Attendance.query.filter_by(status='pendente').count() if session.get('user_role') in {'monitor', 'instrutor'} else 0
    contract_pending = bool(current_user and (
        current_user.membership_terms_version != MEMBERSHIP_TERMS_VERSION
        or current_user.privacy_notice_version != PRIVACY_NOTICE_VERSION
        or current_user.image_consent_scope not in {'adult', 'minor_guardian'}
    ))
    return {
        'now': datetime.utcnow(),
        'is_logged_in': 'user_id' in session,
        'user_name': session.get('user_name', ''),
        'username': session.get('username', ''),
        'user_role': session.get('user_role', 'aluno'),
        'user_plan': session.get('user_plan', ''),
        'user_due_date': session.get('user_due_date', '15'),
        'user_belt_color': current_user.belt_color if current_user else 'branca',
        'user_belt_degree': current_user.belt_degree if current_user else 0,
        'pending_attendance_count': pending_attendance_count,
        'contract_pending': contract_pending,
        'csrf_token': csrf_token
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

@app.route('/loja')
@app.route('/loja.html')
def loja():
    categories = sorted({product['category'] for product in STORE_PRODUCTS})
    return render_template('loja.html', page_title='Loja Oficial', products=STORE_PRODUCTS,
                           store_categories=categories)

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

    if booking_user and booking_user.has_overdue_payments():
        return jsonify({
            'error': 'Reserva bloqueada: existem mensalidades pendentes. Regularize o financeiro para agendar novas aulas.',
            'code': 'payment_required'
        }), 403

    booking = Booking(login_or_name=login_or_name[:120], cpf3=cpf3 or None,
                      modality=modality[:100], shift_time=shift_time[:150],
                      is_experimental=is_experimental)
    db.session.add(booking)
    db.session.commit()
    return jsonify({'id': booking.id}), 201

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
                flash(f'Bem-vindo(a), {user.name}! Login realizado com sucesso.', 'success')
                next_url = request.args.get('next', '')
                if next_url and next_url.startswith('/') and not next_url.startswith('//'):
                    return redirect(next_url)
                return redirect(url_for('dashboard'))
            
            flash('Usuário/CPF ou senha inválidos. Use seu nome de usuário (ex: "fernandovier" ou "bolivarbjj") e a senha "123456".', 'error')
            return redirect(url_for('login'))

        elif action == 'register':
            username = request.form.get('regUsername', '').strip()
            name = request.form.get('regName', '').strip()
            cpf = request.form.get('regCpf', '').strip()
            ddd = request.form.get('regDDD', '').strip()
            phone = request.form.get('regPhoneNumber', '').strip()
            email = request.form.get('regEmail', '').strip().casefold()
            sex = request.form.get('regSex', 'prefer_not').strip()
            plan = request.form.get('regPlan', '').strip()
            due_date = request.form.get('regDueDate', '5').strip()
            password = request.form.get('regPass', '')
            accepted_membership_terms = request.form.get('acceptMembershipTerms') == 'on'
            acknowledged_privacy = request.form.get('acknowledgePrivacy') == 'on'
            accepted_legal_capacity = request.form.get('confirmLegalCapacity') == 'on'
            image_consent_scope = request.form.get('imageConsentScope', '')
            guardian_name = request.form.get('imageGuardianName', '').strip()
            guardian_cpf = request.form.get('imageGuardianCpf', '').strip()
            guardian_relationship = request.form.get('imageGuardianRelationship', '').strip()
            image_use_consent = image_consent_scope in {'adult', 'minor_guardian'}

            cpf_digits = ''.join(c for c in cpf if c.isdigit())
            errors = []
            if not re.fullmatch(r'[A-Za-z0-9_.-]{3,80}', username): errors.append('Usuário deve ter de 3 a 80 caracteres válidos.')
            if len(name) < 3: errors.append('Informe o nome completo.')
            if not is_valid_cpf(cpf_digits): errors.append('CPF inválido.')
            if not re.fullmatch(r'\d{2}', ddd) or not re.fullmatch(r'\d{9}', phone): errors.append('Telefone inválido.')
            if len(email) > 254 or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email): errors.append('Informe um e-mail válido.')
            if sex not in {'masculino', 'feminino', 'prefer_not'}: errors.append('Escolha uma opção válida para sexo.')
            if due_date not in {'5', '15', '25'}: errors.append('Vencimento inválido.')
            if len(password) < 8: errors.append('A senha deve ter pelo menos 8 caracteres.')
            if not accepted_membership_terms: errors.append('Leia e aceite o termo de adesão para concluir a matrícula.')
            if not acknowledged_privacy: errors.append('Confirme a ciência do aviso de privacidade.')
            if not accepted_legal_capacity: errors.append('Confirme que você é maior de 18 anos ou responsável legal pelo aluno.')
            if image_consent_scope not in {'adult', 'minor_guardian'}:
                errors.append('Para concluir o cadastro, autorize o uso de imagem como aluno adulto ou responsável legal pelo menor.')
            if image_consent_scope == 'minor_guardian':
                guardian_cpf_digits = ''.join(character for character in guardian_cpf if character.isdigit())
                if len(guardian_name) < 3: errors.append('Informe o nome completo do responsável pela autorização de imagem do menor.')
                if not is_valid_cpf(guardian_cpf_digits): errors.append('Informe um CPF válido para o responsável pela autorização de imagem.')
                if guardian_relationship not in {'mae', 'pai', 'responsavel_legal'}:
                    errors.append('Informe o vínculo do responsável legal pelo menor.')
            valid_plans = {f'{p.name} — {p.price}' for p in Plan.query.all()}
            if plan not in valid_plans: errors.append('Plano inválido.')
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
                    payment_status='Em Dia',
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
                    user.due_date = new_due_date
                    db.session.commit()
                    session['user_due_date'] = new_due_date
                    flash(f'Dia de vencimento alterado para Dia {new_due_date}!', 'success')
            return redirect(url_for('mensalidades_aluno'))

    if request.args.get('logout') == '1' or request.args.get('switch') == '1':
        session.clear()

    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    return render_template('login.html', page_title='Área de Membros', is_logged_in=False,
                           available_plans=Plan.query.order_by(Plan.category, Plan.id).all(),
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
    has_overdue = user.has_overdue_payments()
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
        existing = Attendance.query.filter_by(user_id=session['user_id'], training_date=datetime.now().date()).first()
        if existing:
            if existing.status == 'confirmado':
                message = 'Sua presença de hoje já foi confirmada.'
            elif existing.status == 'negado':
                message = 'Seu check-in de hoje não foi confirmado pelo instrutor.'
            else:
                message = 'Seu check-in de hoje já está aguardando confirmação do instrutor.'
            flash(message, 'info')
        else:
            active_enrollment = next((item for item in user.class_enrollments if item.active), None)
            db.session.add(Attendance(
                user_id=session['user_id'], status='pendente',
                modality=active_enrollment.class_group.modality if active_enrollment else get_attendance_modality(user.plan),
                class_group_id=active_enrollment.class_group_id if active_enrollment else None,
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
    elif 'passe livre' in normalized_plan:
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
    recent_attendances = confirmed_query.order_by(
        Attendance.training_date.desc()
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
                           today_attendance=today_attendance,
                           pending_confirmations=pending_confirmations,
                           pending_confirmation_groups=pending_confirmation_groups)

@app.route('/treinoteca')
@app.route('/treinoteca.html')
@login_required
def treinoteca():
    return render_template('treinoteca.html', page_title='Treinoteca / Vídeo Aulas')

@app.route('/mensalidades_aluno', methods=['GET', 'POST'])
@app.route('/mensalidades_aluno.html', methods=['GET', 'POST'])
@login_required
def mensalidades_aluno():
    if request.method == 'POST':
        new_due_date = request.form.get('due_date', '15')
        if new_due_date in {'5', '15', '25'}:
            user = db.session.get(User, session['user_id'])
            user.due_date = new_due_date
            db.session.commit()
            session['user_due_date'] = new_due_date
            flash(f'Data de vencimento atualizada para o Dia {new_due_date} de cada mês!', 'success')
        return redirect(url_for('mensalidades_aluno'))
    user = db.session.get(User, session['user_id'])
    overdue = user.get_overdue_details()
    return render_template('mensalidades_aluno.html', page_title='Minhas Mensalidades',
                           finance_user=user, overdue=overdue,
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
            amount = float(payment.amount) if payment and payment_status == 'pago' else user.get_numeric_price(selected_year, month)
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

@app.route('/planos_admin', methods=['GET', 'POST'])
@app.route('/planos_admin.html', methods=['GET', 'POST'])
@role_required('instrutor')
def planos_admin():
    if request.method == 'POST':
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
                flash(f'Plano #{plan.id} removido do sistema.', 'info')
        return redirect(url_for('planos_admin'))

    plans_list = Plan.query.order_by(Plan.id.asc()).all()
    return render_template('planos_admin.html', page_title='Gestão de Planos', plans=plans_list)

@app.route('/gestao/turmas', methods=['GET', 'POST'])
@app.route('/gestao/turmas.html', methods=['GET', 'POST'])
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
        capacity = request.form.get('class_capacity', type=int)
        duration = request.form.get('class_duration', type=int)
        status = request.form.get('class_status', 'ativa')
        duplicate = ClassGroup.query.filter(ClassGroup.name == name)
        if action == 'update':
            duplicate = duplicate.filter(ClassGroup.id != class_group.id)
        if (not name or modality not in {'Jiu-Jitsu', 'Boxe', 'Muay Thai'}
                or audience not in {'Adulto', 'Kids', 'Todos'} or not schedules
                or not instructor or not capacity or not 1 <= capacity <= 100
                or duration not in {45, 60, 75, 90, 120}
                or status not in {'ativa', 'lotada', 'rascunho', 'suspensa'}):
            flash('Revise os campos obrigatórios da turma.', 'error')
            return redirect(url_for('gestao_turmas'))
        if duplicate.first():
            flash('Já existe uma turma cadastrada com esse nome.', 'error')
            return redirect(url_for('gestao_turmas'))
        class_group.name = name
        class_group.modality = modality
        class_group.audience = audience
        class_group.schedules = schedules
        class_group.instructor = instructor
        class_group.capacity = capacity
        class_group.duration_minutes = duration
        class_group.status = status
        class_group.publish_public = request.form.get('publish_public') == '1'
        if action == 'create':
            db.session.add(class_group)
        db.session.commit()
        flash(f'Turma {class_group.name} salva com sucesso!', 'success')
        return redirect(url_for('gestao_turmas'))

    search_query = request.args.get('q', '').strip()
    modality_filter = request.args.get('modality', 'todas')
    status_filter = request.args.get('status', 'todos')
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
    classes = query.order_by(ClassGroup.modality, ClassGroup.name).all()

    all_classes = ClassGroup.query.order_by(ClassGroup.id).all()
    total_capacity = sum(item.capacity for item in all_classes)
    total_enrolled = sum(item.enrolled for item in all_classes)
    overview = {
        'classes': len(all_classes),
        'weekly_sessions': sum(item.weekly_sessions for item in all_classes),
        'enrolled': total_enrolled,
        'occupancy': round(total_enrolled / total_capacity * 100) if total_capacity else 0,
        'waiting': sum(item.waiting for item in all_classes),
    }
    return render_template(
        'gestao_turmas.html', page_title='Gestão de Turmas', classes=classes, overview=overview,
        search_query=search_query, modality_filter=modality_filter, status_filter=status_filter,
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
    )

@app.route('/api/update_month_status', methods=['POST'])
@role_required('instrutor')
def api_update_month_status():
    user_id = request.form.get('user_id')
    month = request.form.get('month')
    status = request.form.get('status')
    
    user = db.session.get(User, user_id)
    year = request.form.get('year', type=int) or datetime.now().year
    if user and month and month.isdigit() and 1 <= int(month) <= 12 and status in ['pago', 'atrasado', 'futuro']:
        user.set_month_status(month, status, year)
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
        
        if action == 'toggle_exemption':
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
                if new_due_date in {'5', '15', '25'}: user.due_date = new_due_date
                db.session.commit()
                flash(f'Mensalidade de {user.name} atualizada! Vencimento: Dia {user.due_date} | Status: {user.payment_status}', 'success')
        
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

    if filter_day in ['5', '15', '25']:
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
    day5_count = User.query.filter_by(due_date='5').count()
    day15_count = User.query.filter_by(due_date='15').count()
    day25_count = User.query.filter_by(due_date='25').count()
    paid_count = User.query.filter_by(payment_status='Em Dia', monthly_fee_exempt=False).count()
    pending_count = User.query.filter_by(payment_status='Pendente', monthly_fee_exempt=False).count()
    exempt_count = User.query.filter_by(monthly_fee_exempt=True).count()
    current_period = datetime.now()

    return render_template(
        'mensalidades_admin.html',
        page_title='Gestão de Mensalidades (30 Alunos)',
        users=users_list,
        filter_day=filter_day,
        search_query=search_query,
        status_filter=status_filter,
        modality_filter=modality_filter,
        total_count=total_count,
        day5_count=day5_count,
        day15_count=day15_count,
        day25_count=day25_count,
        paid_count=paid_count,
        pending_count=pending_count,
        exempt_count=exempt_count,
        report_period_start=f'{current_period.year}-01',
        report_period_end=f'{current_period.year}-{current_period.month:02d}'
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

@app.route('/configuracoes', methods=['GET', 'POST'])
@app.route('/configuracoes.html', methods=['GET', 'POST'])
@login_required
def configuracoes():
    if request.method == 'POST':
        new_name = request.form.get('name', '').strip()
        new_phone = request.form.get('phone', '').strip()
        new_belt_color = request.form.get('belt_color', '').strip().lower()
        new_belt_degree = request.form.get('belt_degree', type=int)
        phone_digits = ''.join(c for c in new_phone if c.isdigit())
        user = db.session.get(User, session['user_id'])
        if new_name and len(phone_digits) in {11, 13}:
            local = phone_digits[-11:]
            user.name, user.ddd, user.phone = new_name, local[:2], local[2:]
            if new_belt_color in BELT_COLORS:
                user.belt_color = new_belt_color
            if new_belt_degree is not None and 0 <= new_belt_degree <= 4:
                user.belt_degree = new_belt_degree
            db.session.commit()
            session['user_name'] = new_name
            flash('Configurações salvas com sucesso!', 'success')
        else:
            flash('Nome ou telefone inválido.', 'error')
        return redirect(url_for('configuracoes'))
    user = db.session.get(User, session['user_id'])
    return render_template('configuracoes.html', page_title='Configurações & Perfil', profile_user=user)

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
