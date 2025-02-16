import os
import secrets
from flask import Flask, render_template
from flask_login import LoginManager, login_required, current_user
from flask_socketio import SocketIO, send
from .routes import auth
from .models import User
from .database import init_db, get_user_by_id

app = Flask(__name__, template_folder='../templates', static_folder='../static')

# Gere uma chave secreta segura!
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or secrets.token_urlsafe(32)

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

app.register_blueprint(auth)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

socketio = SocketIO(app)

@login_manager.user_loader
def load_user(user_id):
    user = get_user_by_id(user_id)
    return user  # Simplificado e corrigido

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@socketio.on('connect')
def handle_connect():
    if current_user.is_authenticated:
        send(f'{current_user.username} conectado.', broadcast=True)

if __name__ == '__main__':
    init_db(app)  # Passe o app para init_db
    socketio.run(app, debug=True)  # debug=True para hot-reload