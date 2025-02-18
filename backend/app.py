from flask import Flask
from flask_socketio import SocketIO
from backend.database import init_db
from backend.routes import configure_routes  # Importação correta

app = Flask(__name__, template_folder='../templates')
app.secret_key = 'your_secret_key'
socketio = SocketIO(app)

init_db()
configure_routes(app, socketio)  # Inicializa as rotas aqui

if __name__ == '__main__':
    socketio.run(app, debug=True, use_reloader=False)