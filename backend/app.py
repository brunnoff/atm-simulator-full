from flask import Flask, render_template
from flask_login import LoginManager, login_required, current_user
from flask_socketio import SocketIO, send
from .routes import auth
from .models import User
from .database import init_db, get_user_by_id

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.config['SECRET_KEY'] = 'sua_chave_secreta'
app.register_blueprint(auth)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

socketio = SocketIO(app)

@login_manager.user_loader
def load_user(user_id):
    user = get_user_by_id(user_id)
    if user:
        return User(user[0], user[1], user[2])
    return None

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
    init_db()
    socketio.run(app)