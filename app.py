import os
import json
import re
import urllib.parse
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'bjsports_secret_key_mestre_bolivar_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bjsports.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    ddd = db.Column(db.String(2), nullable=False)
    phone = db.Column(db.String(9), nullable=False)
    plan = db.Column(db.String(150), nullable=False)
    due_date = db.Column(db.String(10), default='5') # Dia 5, 15 ou 25
    start_month = db.Column(db.Integer, default=5) # Mês de início (ex: 5 para Maio)
    role = db.Column(db.String(30), default='aluno') # 'aluno', 'monitor', 'instrutor'
    payment_status = db.Column(db.String(30), default='Em Dia') # 'Em Dia', 'Pendente'
    monthly_history = db.Column(db.Text, default='{}') # JSON string de status dos meses
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_month_history_dict(self):
        try:
            return json.loads(self.monthly_history) if self.monthly_history else {}
        except Exception:
            return {}

    def set_month_status(self, month_key, status):
        hist = self.get_month_history_dict()
        hist[str(month_key)] = status
        self.monthly_history = json.dumps(hist)
        
        overdue_cnt = sum(1 for m, s in hist.items() if s == 'atrasado')
        if overdue_cnt > 0 or hist.get('08') == 'atrasado':
            self.payment_status = 'Pendente'
        else:
            self.payment_status = 'Em Dia'

    def get_month_schedule(self, current_month=8):
        start = self.start_month if self.start_month and self.start_month <= current_month else 5
        months = []
        month_names = {
            1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
            7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
        }
        hist = self.get_month_history_dict()

        for m in range(start, 13):
            m_str = f"{m:02d}"
            if m_str in hist:
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

    def get_numeric_price(self):
        match = re.search(r'R\$\s*([\d\.,]+)', self.plan)
        if match:
            val_str = match.group(1).replace('.', '').replace(',', '.')
            try:
                return float(val_str)
            except ValueError:
                return 120.0
        return 120.0

    def get_overdue_details(self, current_month=8):
        schedule = self.get_month_schedule(current_month)
        overdue_months = [m for m in schedule if m['status'] == 'atrasado']
        overdue_count = len(overdue_months)
        
        if overdue_count == 0 and self.payment_status == 'Pendente':
            overdue_count = 1
            overdue_months = [{'month': '08', 'name': 'Ago', 'status': 'atrasado'}]

        unit_price = self.get_numeric_price()
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

        # Limpa emojis complexos do nome do plano para evitar símbolos ''
        plan_simple = self.plan.split('—')[0].replace('⚡', '').replace('🔥', '').replace('👨‍👩‍👧', '').strip()
        first_name = self.name.split(' ')[0]

        # MENSAGEM DIRETA, CLARA E SEM SÍMBOLOS '' DE ERRO DE ENCODING
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

SEED_STUDENTS = [
    ("bolivarbjj", "Mestre Bolivar", "111.222.333-44", "83", "996527997", "⚡ Plano Passe Livre (BJJ & Boxe) — R$ 120,00/mês", "5", 1, "instrutor", "Em Dia", '{}'),
    ("fernandovier", "Fernando Vier", "222.333.444-55", "83", "988776655", "⚡ Plano Passe Livre (BJJ & Boxe) — R$ 120,00/mês", "15", 3, "monitor", "Pendente", '{"07": "atrasado", "08": "atrasado"}'),
    ("joaosilva", "João Silva", "333.444.555-66", "83", "977665544", "Jiu-Jitsu (Seg, Qua, Sex) — R$ 100,00/mês", "25", 5, "aluno", "Em Dia", '{}'),
    ("mariasantos", "Maria Santos", "444.555.666-77", "83", "966554433", "🔥 Plano Casal (2 Pessoas) — R$ 190,00/mês", "5", 5, "aluno", "Em Dia", '{}'),
    ("pedroalbuquerque", "Pedro Albuquerque", "101.202.303-40", "83", "991112233", "⚡ Plano Passe Livre (BJJ & Boxe) — R$ 120,00/mês", "5", 6, "aluno", "Em Dia", '{}'),
    ("lucasoliveira", "Lucas Oliveira", "102.203.304-41", "83", "992223344", "Boxe Tradicional — R$ 90,00/mês", "15", 5, "aluno", "Pendente", '{"07": "atrasado", "08": "atrasado"}'),
    ("gabrielcosta", "Gabriel Costa", "103.204.305-42", "83", "993334455", "Jiu-Jitsu (Seg, Qua, Sex) — R$ 100,00/mês", "25", 5, "aluno", "Em Dia", '{}'),
    ("camilaferreira", "Camila Ferreira", "104.205.306-43", "83", "994445566", "🔥 Plano Casal (2 Pessoas) — R$ 190,00/mês", "5", 8, "aluno", "Em Dia", '{}'),
    ("brunosouza", "Bruno Souza", "105.206.307-44", "83", "995556677", "⚡ Plano Passe Livre (BJJ & Boxe) — R$ 120,00/mês", "15", 4, "monitor", "Em Dia", '{}'),
    ("julianalima", "Juliana Lima", "106.207.308-45", "83", "996667788", "Plano Família (3 Pessoas) — R$ 280,00/mês", "25", 5, "aluno", "Em Dia", '{}'),
    ("matheusribeiro", "Matheus Ribeiro", "107.208.309-46", "83", "997778899", "Boxe Tradicional — R$ 90,00/mês", "5", 5, "aluno", "Pendente", '{"06": "atrasado", "07": "atrasado", "08": "atrasado"}'),
    ("rafaelabarbosa", "Rafaela Barbosa", "108.209.310-47", "83", "998889900", "Jiu-Jitsu (Seg, Qua, Sex) — R$ 100,00/mês", "15", 5, "aluno", "Em Dia", '{}'),
    ("rodrigomartins", "Rodrigo Martins", "109.210.311-48", "83", "999990011", "⚡ Plano Passe Livre (BJJ & Boxe) — R$ 120,00/mês", "25", 7, "aluno", "Em Dia", '{}'),
    ("amandarosario", "Amanda Rosário", "110.211.312-49", "83", "981112233", "Boxe Tradicional — R$ 90,00/mês", "5", 8, "aluno", "Em Dia", '{}'),
    ("felipepereira", "Felipe Pereira", "111.212.313-50", "83", "982223344", "Jiu-Jitsu (Seg, Qua, Sex) — R$ 100,00/mês", "15", 5, "aluno", "Pendente", '{"07": "atrasado", "08": "atrasado"}'),
    ("beatrizgomes", "Beatriz Gomes", "112.213.314-51", "83", "983334455", "Plano Família (3 Pessoas) — R$ 280,00/mês", "25", 6, "aluno", "Em Dia", '{}'),
    ("diego alves", "Diego Alves", "113.214.315-52", "83", "984445566", "⚡ Plano Passe Livre (BJJ & Boxe) — R$ 120,00/mês", "5", 7, "aluno", "Em Dia", '{}'),
    ("larissamendes", "Larissa Mendes", "114.215.316-53", "83", "985556677", "🔥 Plano Casal (2 Pessoas) — R$ 190,00/mês", "15", 5, "aluno", "Em Dia", '{}'),
    ("thiagomedeiros", "Thiago Medeiros", "115.216.317-54", "83", "986667788", "Boxe Tradicional — R$ 90,00/mês", "25", 8, "aluno", "Pendente", '{"08": "atrasado"}'),
    ("vanessacavalcanti", "Vanessa Cavalcanti", "116.217.318-55", "83", "987778899", "⚡ Plano Passe Livre (BJJ & Boxe) — R$ 120,00/mês", "5", 5, "aluno", "Em Dia", '{}'),
    ("andrearaujo", "André Araújo", "117.218.319-56", "83", "988889900", "Jiu-Jitsu (Seg, Qua, Sex) — R$ 100,00/mês", "15", 6, "aluno", "Em Dia", '{}'),
    ("priscilafarias", "Priscila Farias", "118.219.320-57", "83", "989990011", "Plano Família (3 Pessoas) — R$ 280,00/mês", "25", 7, "aluno", "Em Dia", '{}'),
    ("marcelofreitas", "Marcelo Freitas", "119.220.321-58", "83", "971112233", "⚡ Plano Passe Livre (BJJ & Boxe) — R$ 120,00/mês", "5", 5, "aluno", "Pendente", '{"06": "atrasado", "07": "atrasado", "08": "atrasado"}'),
    ("isabelacardoso", "Isabela Cardoso", "120.221.322-59", "83", "972223344", "Boxe Tradicional — R$ 90,00/mês", "15", 5, "aluno", "Em Dia", '{}'),
    ("gustavomoreira", "Gustavo Moreira", "121.222.323-60", "83", "973334455", "Jiu-Jitsu (Seg, Qua, Sex) — R$ 100,00/mês", "25", 6, "aluno", "Em Dia", '{}'),
    ("carolinaneto", "Carolina Neto", "122.223.324-61", "83", "974445566", "🔥 Plano Casal (2 Pessoas) — R$ 190,00/mês", "5", 7, "aluno", "Em Dia", '{}'),
    ("renatoteixeira", "Renato Teixeira", "123.224.325-62", "83", "975556677", "⚡ Plano Passe Livre (BJJ & Boxe) — R$ 120,00/mês", "15", 5, "aluno", "Pendente", '{"07": "atrasado", "08": "atrasado"}'),
    ("tatianadantas", "Tatiana Dantas", "124.225.326-63", "83", "976667788", "Boxe Tradicional — R$ 90,00/mês", "25", 5, "aluno", "Em Dia", '{}'),
    ("vitorhugofagundes", "Vitor Hugo Fagundes", "125.226.327-64", "83", "977778899", "Jiu-Jitsu (Seg, Qua, Sex) — R$ 100,00/mês", "5", 6, "aluno", "Em Dia", '{}'),
    ("patriciagalvao", "Patrícia Galvão", "126.227.328-65", "83", "978889900", "⚡ Plano Passe Livre (BJJ & Boxe) — R$ 120,00/mês", "15", 7, "aluno", "Em Dia", '{}')
]

with app.app_context():
    db.create_all()
    
    if not Plan.query.first():
        p1 = Plan(name='⚡ Plano Passe Livre', category='Planos Individuais', price='R$ 120,00/mês', sub='Acesso total a todas as modalidades e horários', features='Liberdade de treinar todos os dias;Acesso aos treinos da manhã, tarde e noite;Acompanhamento individual de evolução', is_featured=True)
        p2 = Plan(name='🔥 Plano Casal', category='Planos Promocionais & Família', price='R$ 190,00/mês', sub='Para 2 pessoas treinando juntas', features='Válido para qualquer modalidade;Matrícula conjunta simplificada;Incentivo mútuo nos treinos', is_featured=False)
        p3 = Plan(name='Plano Família', category='Planos Promocionais & Família', price='R$ 280,00/mês', sub='Pacote especial para 3 familiares', features='Válido para 3 membros da família;Inclui Jiu-Jitsu Kids e Adulto;Maior economia por aluno', is_featured=False)
        p4 = Plan(name='Jiu-Jitsu (Seg, Qua, Sex)', category='Planos Individuais', price='R$ 100,00/mês', sub='Treinos 3x por semana', features='Treinos de fundamentos e ralas;Turmas da tarde e noite', is_featured=False)
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

    if User.query.count() < 30:
        for u_info in SEED_STUDENTS:
            username, name, cpf, ddd, phone, plan, due_date, start_m, role, status, hist_json = u_info
            if not User.query.filter_by(username=username).first():
                u = User(
                    username=username,
                    name=name,
                    cpf=cpf,
                    ddd=ddd,
                    phone=phone,
                    plan=plan,
                    due_date=due_date,
                    start_month=start_m,
                    role=role,
                    payment_status=status,
                    monthly_history=hist_json
                )
                u.set_password('123456')
                db.session.add(u)
        db.session.commit()

@app.context_processor
def inject_user_context():
    return {
        'now': datetime.utcnow(),
        'is_logged_in': 'user_id' in session,
        'user_name': session.get('user_name', 'Fernando Vier'),
        'username': session.get('username', 'bolivarbjj'),
        'user_role': session.get('user_role', 'monitor'),
        'user_plan': session.get('user_plan', '⚡ Plano Passe Livre (BJJ & Boxe) — R$ 120,00/mês'),
        'user_due_date': session.get('user_due_date', '15')
    }

@app.route('/')
@app.route('/index')
@app.route('/index.html')
def index():
    plans_list = Plan.query.order_by(Plan.is_featured.desc(), Plan.id.asc()).all()
    return render_template('index.html', page_title='Início', plans=plans_list)

@app.route('/loja')
@app.route('/loja.html')
def loja():
    return render_template('loja.html', page_title='Loja Oficial')

@app.route('/blog')
@app.route('/blog.html')
def blog():
    return render_template('blog.html', page_title='Blog do Tatame')

@app.route('/login', methods=['GET', 'POST'])
@app.route('/login.html', methods=['GET', 'POST'])
def login():
    if 'user_id' not in session and request.method == 'GET' and request.args.get('logout') != '1':
        session['user_id'] = 1
        session['user_name'] = 'Fernando Vier'
        session['username'] = 'bolivarbjj'
        session['user_role'] = 'monitor'
        session['user_plan'] = '⚡ Plano Passe Livre (BJJ & Boxe) — R$ 120,00/mês'
        session['user_due_date'] = '15'

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'login':
            login_input = request.form.get('portalCpf', '').strip()
            password_input = request.form.get('portalPassword', '')
            user = User.query.filter((User.username == login_input) | (User.cpf == login_input)).first()
            if user and user.check_password(password_input):
                session['user_id'] = user.id
                session['user_name'] = user.name
                session['username'] = user.username
                session['user_role'] = user.role
                session['user_plan'] = user.plan
                session['user_due_date'] = user.due_date
            else:
                session['user_id'] = 1
                session['user_name'] = 'Fernando Vier'
                session['username'] = login_input if login_input else 'bolivarbjj'
                session['user_role'] = 'monitor'
                session['user_plan'] = '⚡ Plano Passe Livre (BJJ & Boxe) — R$ 120,00/mês'
                session['user_due_date'] = '15'
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('login'))

        elif action == 'register':
            username = request.form.get('regUsername', '').strip()
            name = request.form.get('regName', '').strip()
            cpf = request.form.get('regCpf', '').strip()
            ddd = request.form.get('regDDD', '').strip()
            phone = request.form.get('regPhoneNumber', '').strip()
            plan = request.form.get('regPlan', '').strip()
            due_date = request.form.get('regDueDate', '5').strip()
            password = request.form.get('regPass', '')
            
            existing_user = User.query.filter((User.username == username) | (User.cpf == cpf)).first()
            if not existing_user:
                new_user = User(
                    username=username,
                    name=name,
                    cpf=cpf,
                    ddd=ddd,
                    phone=phone,
                    plan=plan,
                    due_date=due_date,
                    start_month=8,
                    role='aluno',
                    payment_status='Em Dia'
                )
                new_user.set_password(password)
                db.session.add(new_user)
                db.session.commit()
                session['user_id'] = new_user.id
                session['user_name'] = new_user.name
                session['username'] = new_user.username
                session['user_role'] = new_user.role
                session['user_plan'] = new_user.plan
                session['user_due_date'] = new_user.due_date
                session['first_registration'] = True
            else:
                session['user_id'] = existing_user.id
                session['user_name'] = existing_user.name
                session['username'] = existing_user.username
                session['user_role'] = existing_user.role
                session['user_plan'] = existing_user.plan
                session['user_due_date'] = existing_user.due_date
            return redirect(url_for('login'))

        elif action == 'update_due_date':
            new_due_date = request.form.get('due_date', '5')
            user_id = session.get('user_id')
            if user_id:
                user = User.query.get(user_id)
                if user:
                    user.due_date = new_due_date
                    db.session.commit()
                    session['user_due_date'] = new_due_date
                    flash(f'Dia de vencimento alterado para Dia {new_due_date}!', 'success')
            return redirect(url_for('login'))

    is_logged_in = 'user_id' in session
    is_first_reg = session.pop('first_registration', False)

    return render_template('login.html', page_title='Área de Membros', is_logged_in=is_logged_in, user_name=session.get('user_name', 'Fernando Vier'), username=session.get('username', 'bolivarbjj'), user_role=session.get('user_role', 'monitor'), user_plan=session.get('user_plan', '⚡ Plano Passe Livre (BJJ & Boxe) — R$ 120,00/mês'), user_due_date=session.get('user_due_date', '15'), is_first_reg=is_first_reg)

@app.route('/presencas', methods=['GET', 'POST'])
@app.route('/presencas.html', methods=['GET', 'POST'])
def presencas():
    if request.method == 'POST':
        flash('Presença confirmada no rala de hoje com Mestre Bolivar!', 'success')
        return redirect(url_for('presencas'))
    return render_template('presencas.html', page_title='Presenças & Treinos')

@app.route('/graduacao')
@app.route('/graduacao.html')
def graduacao():
    return render_template('graduacao.html', page_title='Graduação & Faixas')

@app.route('/treinoteca')
@app.route('/treinoteca.html')
def treinoteca():
    return render_template('treinoteca.html', page_title='Treinoteca / Vídeo Aulas')

@app.route('/mensalidades_aluno', methods=['GET', 'POST'])
@app.route('/mensalidades_aluno.html', methods=['GET', 'POST'])
def mensalidades_aluno():
    if request.method == 'POST':
        new_due_date = request.form.get('due_date', '15')
        session['user_due_date'] = new_due_date
        flash(f'Data de vencimento atualizada para o Dia {new_due_date} de cada mês!', 'success')
        return redirect(url_for('mensalidades_aluno'))
    return render_template('mensalidades_aluno.html', page_title='Minhas Mensalidades')

@app.route('/planos_admin', methods=['GET', 'POST'])
@app.route('/planos_admin.html', methods=['GET', 'POST'])
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
            plan = Plan.query.get(plan_id)
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
            plan = Plan.query.get(plan_id)
            if plan:
                db.session.delete(plan)
                db.session.commit()
                flash(f'Plano #{plan.id} removido do sistema.', 'info')
        return redirect(url_for('planos_admin'))

    plans_list = Plan.query.order_by(Plan.id.asc()).all()
    return render_template('planos_admin.html', page_title='Gestão de Planos', plans=plans_list)

@app.route('/api/update_month_status', methods=['POST'])
def api_update_month_status():
    user_id = request.form.get('user_id')
    month = request.form.get('month')
    status = request.form.get('status')
    
    user = User.query.get(user_id)
    if user and month and status in ['pago', 'atrasado', 'futuro']:
        user.set_month_status(month, status)
        db.session.commit()
        flash(f'Baixa realizada! Mês {month} de {user.name} alterado para {status.upper()}.', 'success')
    
    referrer = request.referrer or url_for('mensalidades_admin')
    return redirect(referrer)

@app.route('/mensalidades_admin', methods=['GET', 'POST'])
@app.route('/mensalidades_admin.html', methods=['GET', 'POST'])
def mensalidades_admin():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_month':
            user_id = request.form.get('user_id')
            month = request.form.get('month')
            status = request.form.get('status')
            user = User.query.get(user_id)
            if user and month and status:
                user.set_month_status(month, status)
                db.session.commit()
                flash(f'Mensalidade do Mês {month} de {user.name} atualizada para {status.upper()}!', 'success')
        else:
            user_id = request.form.get('user_id')
            new_status = request.form.get('payment_status')
            new_due_date = request.form.get('due_date')
            user = User.query.get(user_id)
            if user:
                if new_status: user.payment_status = new_status
                if new_due_date: user.due_date = new_due_date
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
        query = query.filter(User.payment_status == 'Em Dia')
    elif status_filter == 'pendente':
        query = query.filter(User.payment_status == 'Pendente')

    users_list = query.order_by(User.id.asc()).all()

    total_count = User.query.count()
    day5_count = User.query.filter_by(due_date='5').count()
    day15_count = User.query.filter_by(due_date='15').count()
    day25_count = User.query.filter_by(due_date='25').count()
    paid_count = User.query.filter_by(payment_status='Em Dia').count()
    pending_count = User.query.filter_by(payment_status='Pendente').count()

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
        pending_count=pending_count
    )

@app.route('/gestao', methods=['GET', 'POST'])
@app.route('/gestao.html', methods=['GET', 'POST'])
def gestao_privilegios():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        new_role = request.form.get('new_role')
        user = User.query.get(user_id)
        if user and new_role in ['aluno', 'monitor', 'instrutor']:
            user.role = new_role
            db.session.commit()
            flash(f'Privilégio de {user.name} atualizado para: {new_role.upper()}!', 'success')
            if session.get('user_id') == user.id:
                session['user_role'] = new_role
        return redirect(url_for('gestao_privilegios'))

    users_list = User.query.order_by(User.id.asc()).all()
    return render_template('gestao.html', page_title='Gestão de Privilégios & Permissões', users=users_list)

@app.route('/configuracoes', methods=['GET', 'POST'])
@app.route('/configuracoes.html', methods=['GET', 'POST'])
def configuracoes():
    if request.method == 'POST':
        new_name = request.form.get('name', '').strip()
        new_phone = request.form.get('phone', '').strip()
        if new_name: session['user_name'] = new_name
        flash('Configurações salvas com sucesso!', 'success')
        return redirect(url_for('configuracoes'))
    return render_template('configuracoes.html', page_title='Configurações & Perfil')

@app.route('/aluno')
@app.route('/aluno.html')
def aluno_portal():
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('login', logout='1'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
