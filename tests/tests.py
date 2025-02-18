import unittest
from backend.database import SessionLocal, init_db
from backend.models import User, Account
from backend.utils import check_balance

class TestATM(unittest.TestCase):

    def setUp(self):
        init_db()
        self.db = SessionLocal()
        user = User(username="testuser", password="testpass")
        self.db.add(user)
        self.db.commit()
        account = Account(user_id=user.id, balance=100.0)
        self.db.add(account)
        self.db.commit()

    def tearDown(self):
        self.db.close()

    def test_check_balance_sufficient(self):
        account = self.db.query(Account).first()
        self.assertTrue(check_balance(account, 50))

    def test_check_balance_insufficient(self):
        account = self.db.query(Account).first()
        self.assertFalse(check_balance(account, 200))

    def test_user_creation(self):
        user = self.db.query(User).filter_by(username="testuser").first()
        self.assertEqual(user.username, "testuser")

    def test_account_balance_update(self):
        account = self.db.query(Account).first()
        account.balance -= 50
        self.db.commit()
        self.assertEqual(account.balance, 50.0)

if __name__ == '__main__':
    unittest.main()