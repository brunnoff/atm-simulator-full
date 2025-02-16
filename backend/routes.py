from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user
from .models import User
from .database import get_user, add_user

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = get_user(username)
        if user and user[2] == password:
            login_user(User(user[0], user[1], user[2]))
            return redirect(url_for('main.dashboard'))
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
            flash('Usuário registrado com sucesso.')
            return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))