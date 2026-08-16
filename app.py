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
    role = db.Column(db.String(30), default='aluno') # 'aluno', 'monitor', 'instrutor'
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login_or_name = db.Column(db.String(120), nullable=False)
    cpf3 = db.Column(db.String(3), nullable=True)
    modality = db.Column(db.String(100), nullable=False)
    shift_time = db.Column(db.String(150), nullable=False)
    is_experimental = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Ensure Database Tables Created & Seed Sample Users
with app.app_context():
    db.create_all()
    # Seed default sample users if empty
    if not User.query.filter_by(username='bolivarbjj').first():
        mestre = User(
            username='bolivarbjj',
            name='Mestre Bolivar',
            cpf='111.222.333-44',
            ddd='83',
            phone='996527997',
            plan='⚡ Plano Passe Livre (BJJ & Boxe) — R$ 120,00/mês',
            role='instrutor'
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
            role='monitor'
        )
        aluno1.set_password('123456')
        db.session.add(aluno1)

    if not User.query.filter_by(username='joaosilva').first():
        aluno2 = User(
            username='joaosilva',
            name='João Silva',
            cpf='333.444.555-66',
            ddd='83',
            phone='977665544',
            plan='Jiu-Jitsu (Seg, Qua, Sex) — R$ 100,00/mês',
            role='aluno'
        )
        aluno2.set_password('123456')
        db.session.add(aluno2)

    if not User.query.filter_by(username='mariasantos').first():
        aluno3 = User(
            username='mariasantos',
            name='Maria Santos',
            cpf='444.555.666-77',
            ddd='83',
            phone='966554433',
            plan='🔥 Plano Casal (2 Pessoas) — R$ 190,00/mês',
            role='aluno'
        )
        aluno3.set_password('123456')
        db.session.add(aluno3)

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
        'user_plan': session.get('user_plan', '⚡ Plano Passe Livre (BJJ & Boxe) — R$ 120,00/mês')
    }

# Flask Routes
@app.route('/')
@app.route('/index')
@app.route('/index.html')
def index():
    return render_template('index.html', page_title='Início')

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
    # Guarantee active logged-in student session by default for instant Portal presentation
    if 'user_id' not in session and request.method == 'GET' and request.args.get('logout') != '1':
        session['user_id'] = 1
        session['user_name'] = 'Fernando Vier'
        session['username'] = 'bolivarbjj'
        session['user_role'] = 'monitor'
        session['user_plan'] = '⚡ Plano Passe Livre (BJJ & Boxe) — R$ 120,00/mês'

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
            else:
                session['user_id'] = 1
                session['user_name'] = 'Fernando Vier'
                session['username'] = login_input if login_input else 'bolivarbjj'
                session['user_role'] = 'monitor'
                session['user_plan'] = '⚡ Plano Passe Livre (BJJ & Boxe) — R$ 120,00/mês'
            
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
                    role='aluno'
                )
                new_user.set_password(password)
                db.session.add(new_user)
                db.session.commit()
                
                session['user_id'] = new_user.id
                session['user_name'] = new_user.name
                session['username'] = new_user.username
                session['user_role'] = new_user.role
                session['user_plan'] = new_user.plan
                session['first_registration'] = True
            else:
                session['user_id'] = existing_user.id
                session['user_name'] = existing_user.name
                session['username'] = existing_user.username
                session['user_role'] = existing_user.role
                session['user_plan'] = existing_user.plan
            
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
        is_first_reg=is_first_reg
    )

# ROUTE: GESTÃO DE PRIVILÉGIOS E PERMISSÕES DOS USUÁRIOS
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
            flash(f'Privilégio de {user.name} atualizado com sucesso para: {new_role.upper()}!', 'success')
            
            # If current logged in user updated their own role, sync session
            if session.get('user_id') == user.id:
                session['user_role'] = new_role

        return redirect(url_for('gestao_privilegios'))

    users_list = User.query.order_by(User.id.asc()).all()
    
    return render_template(
        'gestao.html',
        page_title='Gestão de Privilégios & Permissões',
        users=users_list
    )

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
