from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

class Account:
    def __init__(self, account_number, balance=0):
        self.account_number = account_number
        self.balance = balance

class BankDatabase:
    def __init__(self):
        self.users = {}
        self.accounts = {}

    def add_user(self, user):
        self.users[user.id] = user

    def add_account(self, account):
        self.accounts[account.account_number] = account

    def get_user(self, username):
        return next((user for user in self.users.values() if user.username == username), None)

    def get_account(self, account_number):
        return self.accounts.get(account_number)