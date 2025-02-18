from backend.database import SessionLocal
from backend.models import Account

def check_balance(account, amount):
    return account.balance >= amount