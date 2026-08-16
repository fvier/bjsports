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

# Ensure Database Tables Created
with app.app_context():
    db.create_all()

# Context Processor for active navigation
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

# Flask Routes supporting both clean URLs and .html extensions
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
    first_registration = False
    
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
                session['user_plan'] = user.plan
                flash('Login realizado com sucesso!', 'success')
                return redirect(url_for('login'))
            else:
                # Demo fallback for testing with bolivarbjj if not in db
                session['user_id'] = 999
                session['user_name'] = 'Fernando Vier'
                session['username'] = login_input if login_input else 'bolivarbjj'
                session['user_plan'] = 'Plano Passe Livre (BJJ & Boxe) — R$ 120,00/mês'
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
                    plan=plan
                )
                new_user.set_password(password)
                db.session.add(new_user)
                db.session.commit()
                
                session['user_id'] = new_user.id
                session['user_name'] = new_user.name
                session['username'] = new_user.username
                session['user_plan'] = new_user.plan
                session['first_registration'] = True
            else:
                session['user_id'] = existing_user.id
                session['user_name'] = existing_user.name
                session['username'] = existing_user.username
                session['user_plan'] = existing_user.plan
            
            return redirect(url_for('login'))

    is_logged_in = 'user_id' in session
    is_first_reg = session.pop('first_registration', False)

    return render_template(
        'login.html',
        page_title='Login & Área de Membros',
        is_logged_in=is_logged_in,
        user_name=session.get('user_name', 'Fernando Vier'),
        username=session.get('username', 'bolivarbjj'),
        user_plan=session.get('user_plan', 'Plano Passe Livre (BJJ & Boxe) — R$ 120,00/mês'),
        is_first_reg=is_first_reg
    )

@app.route('/aluno')
@app.route('/aluno.html')
def aluno_portal():
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
