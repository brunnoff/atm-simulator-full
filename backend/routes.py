from flask import render_template, request, redirect, url_for, session, flash
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
            security_question = request.form.get('security_question', '')
            security_answer = request.form.get('security_answer', '')
            db = next(get_db_session())
            existing_user = db.query(User).filter_by(username=username).first()
            if existing_user:
                flash("Usuário já existe!", 'danger')
                return redirect(url_for('register'))
            new_user = User(username=username, password=password, security_question=security_question, security_answer=security_answer)
            db.add(new_user)
            account = Account(user=new_user, balance=0.0)
            db.add(account)
            db.commit()
            flash("Registro bem-sucedido! Faça login.", 'success')
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
                flash("Login bem-sucedido!", 'success')
                return redirect(url_for('dashboard', username=user.username))
            flash("Credenciais inválidas", 'danger')
            return redirect(url_for('login'))
        return render_template('login.html')

    @app.route('/dashboard/<username>')
    def dashboard(username):
        if 'user_id' in session:
            db = next(get_db_session())
            user = db.query(User).get(session['user_id'])
            return render_template('dashboard.html', user=user)
        return redirect(url_for('login'))

    @app.route('/logout')
    def logout():
        session.pop('user_id', None)
        flash("Logout bem-sucedido!", 'info')
        return redirect(url_for('login'))

    @app.route('/withdraw', methods=['POST'])
    def withdraw():
        if 'user_id' in session:
            db = next(get_db_session())
            user = db.query(User).get(session['user_id'])
            amount = float(request.form['amount'])
            if check_balance(user.account, amount):
                user.account.balance -= amount
                db.commit()
                socketio.emit('update_balance', {'balance': f"{user.account.balance:.2f}"})
                flash("Saque realizado com sucesso!", 'success')
            else:
                flash("Saldo insuficiente!", 'danger')
            return redirect(url_for('dashboard', username=user.username))
        return redirect(url_for('login'))

    @app.route('/deposit', methods=['POST'])
    def deposit():
        if 'user_id' in session:
            db = next(get_db_session())
            user = db.query(User).get(session['user_id'])
            amount = float(request.form['amount'])
            user.account.balance += amount
            db.commit()
            socketio.emit('update_balance', {'balance': f"{user.account.balance:.2f}"})
            flash("Depósito realizado com sucesso!", 'success')
            return redirect(url_for('dashboard', username=user.username))
        return redirect(url_for('login'))

    @app.route('/delete_account', methods=['POST'])
    def delete_account():
        if 'user_id' in session:
            db = next(get_db_session())
            user = db.query(User).get(session['user_id'])
            db.delete(user.account)
            db.delete(user)
            db.commit()
            session.pop('user_id', None)
            flash("Conta excluída com sucesso!", 'info')
        return redirect(url_for('index'))

    @app.route('/transfer', methods=['POST'])
    def transfer():
        if 'user_id' in session:
            db = next(get_db_session())
            sender = db.query(User).get(session['user_id'])
            recipient_username = request.form['recipient']
            amount = float(request.form['amount'])
            recipient = db.query(User).filter_by(username=recipient_username).first()
            if recipient and check_balance(sender.account, amount):
                sender.account.balance -= amount
                recipient.account.balance += amount
                db.commit()
                socketio.emit('update_balance', {'balance': f"{sender.account.balance:.2f}"})
                flash("Transferência realizada com sucesso!", 'success')
            else:
                flash("Usuário não encontrado ou saldo insuficiente!", 'danger')
            return redirect(url_for('dashboard', username=sender.username))
        return redirect(url_for('login'))

    @app.route('/forgot_password', methods=['GET', 'POST'])
    def forgot_password():
        db = next(get_db_session())
        security_question = None
        username = None

        if request.method == 'POST':
            username = request.form['username']
            user = db.query(User).filter_by(username=username).first()
            if user:
                return render_template('forgot_password.html', security_question=user.security_question, username=username)
            else:
                flash("Usuário não encontrado!", 'danger')

        return render_template('forgot_password.html')

    @app.route('/reset_password', methods=['POST'])
    def reset_password():
        db = next(get_db_session())
        username = request.form.get('username')
        if not username:
            flash("Erro: Nome de usuário não encontrado", 'danger')
            return redirect(url_for('forgot_password'))
        security_answer = request.form['security_answer']
        new_password = request.form['new_password']
        user = db.query(User).filter_by(username=username, security_answer=security_answer).first()
        if user:
            user.password = new_password
            db.commit()
            flash("Senha redefinida com sucesso!", 'success')
            return redirect(url_for('login'))
        flash("Resposta de segurança incorreta!", 'danger')
        return redirect(url_for('forgot_password'))

    @socketio.on('message')
    def handle_message(message):
        print('Mensagem recebida:', message)
        socketio.emit('response', {'data': 'Mensagem recebida pelo servidor!'})