from backend.database import SessionLocal
from backend.models import User, Account

def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_balance(account, amount):
    return account.balance >= amount

def find_user_by_username(username):
    db = next(get_db_session())
    user = db.query(User).filter_by(username=username).first()
    db.close()
    return user