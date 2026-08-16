import os
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
    role = db.Column(db.String(30), default='aluno') # 'aluno', 'monitor', 'instrutor'
    payment_status = db.Column(db.String(30), default='Em Dia') # 'Em Dia', 'Pendente'
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Plan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(80), nullable=False) # 'Planos Individuais', 'Planos Promocionais & Família'
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

# Ensure Database Tables Created & Seed Sample Data
with app.app_context():
    db.create_all()
    
    # Seed default sample plans if empty
    if not Plan.query.first():
        p1 = Plan(
            name='⚡ Plano Passe Livre',
            category='Planos Individuais',
            price='R$ 120,00/mês',
            sub='Acesso total a todas as modalidades e horários',
            features='Liberdade de treinar todos os dias;Acesso aos treinos da manhã, tarde e noite;Acompanhamento individual de evolução',
            is_featured=True
        )
        p2 = Plan(
            name='🔥 Plano Casal',
            category='Planos Promocionais & Família',
            price='R$ 190,00/mês',
            sub='Para 2 pessoas treinando juntas',
            features='Válido para qualquer modalidade;Matrícula conjunta simplificada;Incentivo mútuo nos treinos',
            is_featured=False
        )
        p3 = Plan(
            name='Plano Família',
            category='Planos Promocionais & Família',
            price='R$ 280,00/mês',
            sub='Pacote especial para 3 familiares',
            features='Válido para 3 membros da família;Inclui Jiu-Jitsu Kids e Adulto;Maior economia por aluno',
            is_featured=False
        )
        p4 = Plan(
            name='Jiu-Jitsu (Seg, Qua, Sex)',
            category='Planos Individuais',
            price='R$ 100,00/mês',
            sub='Treinos 3x por semana',
            features='Treinos de fundamentos e ralas;Turmas da tarde e noite',
            is_featured=False
        )
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

    # Seed default sample users if empty
    if not User.query.filter_by(username='bolivarbjj').first():
        mestre = User(
            username='bolivarbjj',
            name='Mestre Bolivar',
            cpf='111.222.333-44',
            ddd='83',
            phone='996527997',
            plan='⚡ Plano Passe Livre (BJJ & Boxe) — R$ 120,00/mês',
            due_date='5',
            role='instrutor',
            payment_status='Em Dia'
        )
        mestre.set_password('123456')
        db.session.add(mestre)

    if not User.query.filter_by(username='fernandovier').first():
        aluno1 = User(
            username='fernandovier',
            name='Fernando Vier',
            cpf='222.333.444-55',
            ddd='83',
            phone='988776655',
            plan='⚡ Plano Passe Livre (BJJ & Boxe) — R$ 120,00/mês',
            due_date='15',
            role='monitor',
            payment_status='Em Dia'
        )
        aluno1.set_password('123456')
        db.session.add(aluno1)

    db.session.commit()

# Context Processor for active navigation and user state across all templates
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

# Flask Routes
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
        
        # Action 1: User Login
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

        # Action 2: User Registration
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

        # Action 3: Atualizar Dia de Vencimento
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

    return render_template(
        'login.html',
        page_title='Área de Membros',
        is_logged_in=is_logged_in,
        user_name=session.get('user_name', 'Fernando Vier'),
        username=session.get('username', 'bolivarbjj'),
        user_role=session.get('user_role', 'monitor'),
        user_plan=session.get('user_plan', '⚡ Plano Passe Livre (BJJ & Boxe) — R$ 120,00/mês'),
        user_due_date=session.get('user_due_date', '15'),
        is_first_reg=is_first_reg
    )

# DEDICATED ROUTES FOR EVERY SIDEBAR ITEM

# 1. SEÇÃO AULAS — Presenças & Treinos
@app.route('/presencas', methods=['GET', 'POST'])
@app.route('/presencas.html', methods=['GET', 'POST'])
def presencas():
    if request.method == 'POST':
        flash('Presença confirmada no rala de hoje com Mestre Bolivar!', 'success')
        return redirect(url_for('presencas'))
    return render_template('presencas.html', page_title='Presenças & Treinos')

# 2. SEÇÃO AULAS — Graduação & Faixas
@app.route('/graduacao')
@app.route('/graduacao.html')
def graduacao():
    return render_template('graduacao.html', page_title='Graduação & Faixas')

# 3. SEÇÃO AULAS — Treinoteca / Vídeo Aulas
@app.route('/treinoteca')
@app.route('/treinoteca.html')
def treinoteca():
    return render_template('treinoteca.html', page_title='Treinoteca / Vídeo Aulas')

# 4. SEÇÃO FINANCEIRO — Minhas Mensalidades
@app.route('/mensalidades_aluno', methods=['GET', 'POST'])
@app.route('/mensalidades_aluno.html', methods=['GET', 'POST'])
def mensalidades_aluno():
    if request.method == 'POST':
        new_due_date = request.form.get('due_date', '15')
        session['user_due_date'] = new_due_date
        flash(f'Data de vencimento atualizada para o Dia {new_due_date} de cada mês!', 'success')
        return redirect(url_for('mensalidades_aluno'))
    return render_template('mensalidades_aluno.html', page_title='Minhas Mensalidades')

# 5. SEÇÃO ADMINISTRAÇÃO — Gestão de Planos
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

            new_plan = Plan(
                name=name,
                category=category,
                price=price,
                sub=sub,
                features=features,
                is_featured=is_featured
            )
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

# 6. SEÇÃO ADMINISTRAÇÃO — Gestão de Mensalidades
@app.route('/mensalidades_admin', methods=['GET', 'POST'])
@app.route('/mensalidades_admin.html', methods=['GET', 'POST'])
def mensalidades_admin():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        new_status = request.form.get('payment_status')
        new_due_date = request.form.get('due_date')

        user = User.query.get(user_id)
        if user:
            if new_status: user.payment_status = new_status
            if new_due_date: user.due_date = new_due_date
            db.session.commit()
            flash(f'Mensalidade de {user.name} atualizada! Vencimento: Dia {user.due_date} | Status: {user.payment_status}', 'success')

        return redirect(url_for('mensalidades_admin'))

    users_list = User.query.order_by(User.due_date.asc(), User.id.asc()).all()
    return render_template('mensalidades_admin.html', page_title='Gestão de Mensalidades & Cobrança', users=users_list)

# 7. SEÇÃO ADMINISTRAÇÃO — Gestão de Privilégios
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

# 8. SEÇÃO CONFIGURAÇÕES — Configurações & Perfil
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
