from . import db
from .models import User, Account

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()

def get_user(username):
    return User.query.filter_by(username=username).first()

def add_user(username, password):
    user = User(username=username, password=password)
    db.session.add(user)
    db.session.commit()

def get_user_by_id(user_id):
    return User.query.filter_by(id=user_id).first()

def create_account(user_id):
    account = Account(user_id=user_id)
    db.session.add(account)
    db.session.commit()

def get_account_by_user_id(user_id):
    return Account.query.filter_by(user_id=user_id).first()

def update_account_balance(account_id, balance):
    account = Account.query.filter_by(id=account_id).first()
    if account:
        account.balance = balance
        db.session.commit()