from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from .models import User, Account
from .database import get_user, add_user, get_account_by_user_id, update_account_balance, create_account
from werkzeug.security import check_password_hash

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = get_user(username)
        if user and check_password_hash(user.password, password):
            login_user(user)

            # Verifique se o usuário já tem uma conta
            account = get_account_by_user_id(user.id)
            if not account:
                create_account(user.id)  # Crie a conta se não existir

            return redirect(url_for('auth.dashboard'))
        else:
            flash('Credenciais inválidas. Tente novamente.')
    return render_template('login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if get_user(username):
            flash('Usuário já existe.')
        else:
            add_user(username, password)
            user = get_user(username)  # Obtém o usuário após o registro
            create_account(user.id)  # Cria a conta para o usuário
            flash('Usuário registrado com sucesso.')
            return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/dashboard') # Rota para o dashboard (precisa existir)
@login_required
def dashboard():
    return render_template('dashboard.html')

@auth.route('/consultar_saldo')
@login_required
def consultar_saldo():
    account = get_account_by_user_id(current_user.id)
    if account:
        return jsonify({'success': True, 'saldo': account.balance})
    return jsonify({'success': False, 'message': 'Conta não encontrada'})

@auth.route('/depositar', methods=['POST'])
@login_required
def depositar():
    data = request.get_json()
    valor = data.get('valor')
    account = get_account_by_user_id(current_user.id)
    if account and valor > 0:
        account.balance += valor
        update_account_balance(account.id, account.balance)
        return jsonify({'success': True, 'saldo': account.balance})
    return jsonify({'success': False, 'message': 'Erro ao depositar'})

@auth.route('/sacar', methods=['POST'])
@login_required
def sacar():
    data = request.get_json()
    valor = data.get('valor')
    account = get_account_by_user_id(current_user.id)
    if account and valor > 0 and valor <= account.balance:
        account.balance -= valor
        update_account_balance(account.id, account.balance)
        return jsonify({'success': True, 'saldo': account.balance})
    return jsonify({'success': False, 'message': 'Erro ao sacar'})