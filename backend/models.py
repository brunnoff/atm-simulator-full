from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    account = db.relationship('Account', backref='user', uselist=False)

    def __init__(self, id=None, username=username, password=None):
        self.id = id
        self.username = username
        if password is not None:
            self.password = generate_password_hash(password)

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    balance = db.Column(db.Float, default=0.0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)