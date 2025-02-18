from flask import render_template, request, redirect, url_for, session, jsonify, flash
from backend.database import SessionLocal
from backend.models import User, Account
from backend.utils import check_balance
from flask_socketio import emit

def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def configure_routes(app, socketio):
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            username = request.form['username']
            password = request.form['password']
            db = next(get_db_session())
            existing_user = db.query(User).filter_by(username=username).first()
            if existing_user:
                flash("Usuário já existe!")
                return redirect(url_for('register'))
            new_user = User(username=username, password=password)
            db.add(new_user)
            account = Account(user_id=new_user.id, balance=0.0)
            db.add(account)
            db.commit()
            flash("Registro bem-sucedido! Faça login para continuar.")
            return redirect(url_for('login'))
        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            db = next(get_db_session())
            user = db.query(User).filter_by(username=username, password=password).first()
            if user:
                session['user_id'] = user.id
                return redirect(url_for('dashboard'))
            flash("Credenciais inválidas")
            return redirect(url_for('login'))
        return render_template('login.html')

    @app.route('/dashboard')
    def dashboard():
        if 'user_id' in session:
            db = next(get_db_session())
            user = db.query(User).get(session['user_id'])
            if user.account is None:
                account = Account(user_id=user.id, balance=0.0)
                db.add(account)
                db.commit()
            return render_template('dashboard.html', user=user)
        return redirect(url_for('login'))

    @app.route('/logout')
    def logout():
        session.pop('user_id', None)
        return redirect(url_for('login'))

    @app.route('/withdraw', methods=['POST'])
    def withdraw():
        if 'user_id' in session:
            db = next(get_db_session())
            user = db.query(User).get(session['user_id'])
            if user.account is None:
                flash("Conta não encontrada!")
                return redirect(url_for('dashboard'))
            amount = float(request.form['amount'])
            if check_balance(user.account, amount):
                user.account.balance -= amount
                db.commit()
                socketio.emit('update_balance', {'balance': user.account.balance})
                flash("Saque realizado com sucesso!")
                return redirect(url_for('dashboard'))  # Redireciona para a dashboard
            else:
                flash("Saldo insuficiente!")
                return redirect(url_for('dashboard'))
        flash("Não autorizado!")
        return redirect(url_for('login'))
    
    @app.route('/deposit', methods=['POST'])
    def deposit():
        if 'user_id' in session:
            db = next(get_db_session())
            user = db.query(User).get(session['user_id'])
            if user.account is None:
                flash("Conta não encontrada!")
                return redirect(url_for('dashboard'))
            amount = float(request.form['amount'])
            user.account.balance += amount
            db.commit()
            socketio.emit('update_balance', {'balance': user.account.balance})
            flash("Depósito realizado com sucesso!")
            return redirect(url_for('dashboard'))  # Redireciona para a dashboard
        flash("Não autorizado!")
        return redirect(url_for('login'))

    @socketio.on('message')
    def handle_message(message):
        print('Mensagem recebida:', message)
        socketio.emit('response', {'data': 'Mensagem recebida pelo servidor!'})