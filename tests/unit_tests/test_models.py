import unittest
import mock
from tests import app
from tests.unit_tests.base import DbUnitTestBase
from mtg_api.models.magic import MtgCardModel, MtgCardSetModel
from mtg_api.db import db_instance as db
import datetime
from mtg_api.models.magic import FormatModel

# NOTE: Just using FormatModel as an easy to populate DB model. Any model should work.
class MixinMethodsTestCase(DbUnitTestBase):

    def setUp(self):
        db.make_tables()
        self.load_data()

    def tearDown(self):
        db.drop_tables()

    def load_data(self):
        f = FormatModel()
        f.name = "Test Format"
        db.Session.add(f)
        self.test_format = f

        uf = FormatModel()
        uf.name = "Update This Format"
        db.Session.add(uf)
        self.update_format = uf

        df = FormatModel()
        df.name = "Delete This Format"
        db.Session.add(df)

        db.Session.commit()

    def test_get_or_make(self):
        f = FormatModel.get_or_make(name="Nonexistent Format")
        f2 = db.Session.query(FormatModel).filter(FormatModel.name == "Nonexistent Format").all()
        self.assertEqual(len(f2), 1)
        self.assertEqual(f2[0].id, f.id)

        f3 = FormatModel.get_or_make(name="Nonexistent Format")
        self.assertEqual(len(db.Session.query(FormatModel).filter_by(name="Nonexistent Format").all()), 1)
        self.assertEqual(f3.id, f2[0].id)
        self.assertEqual(f3.id, f.id)

    def test_insert(self):
        f = FormatModel()
        f.name = "Insert Test Model"
        f.insert()

        retrieved_format = db.Session.query(FormatModel).filter_by(name="Insert Test Model").one()
        self.assertEqual(retrieved_format.id, f.id)

    def test_delete(self):
        f = db.Session.query(FormatModel).filter_by(name="Delete This Format").one()
        f.delete()

        f2 = db.Session.query(FormatModel).filter_by(name="Delete This Format").all()
        self.assertEqual(len(f2), 0)

    def test_get(self):
        f = FormatModel.get(self.test_format.id)
        self.assertEqual(f.id, self.test_format.id)

    def test_update(self):
        self.update_format.name = "Updated!"
        self.update_format.update()

        uf = db.Session.query(FormatModel).filter_by(name="Updated!").one()
        self.assertEqual(uf.id, self.update_format.id)
