import unittest
from mtg_api.db import db_instance as db

class DbUnitTestBase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        db.make_database(drop_if_exists=True)

    @classmethod
    def tearDownClass(self):
        db.close()
        db.drop_database()
