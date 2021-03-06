import unittest
import mock
from tests import app
from tests.unit_tests.base import DbUnitTestBase
from mtg_api.api import get_cards_from_properties, get_random_card, get_set
from mtg_api.models.magic import MtgCardModel, MtgCardSetModel
from mtg_api.db import db_instance as db
import datetime


class APICardTestCase(DbUnitTestBase):

    def setUp(self):
        db.make_tables()
        self.load_data()

    def tearDown(self):
        db.drop_tables()

    def load_data(self):
        db.base.metadata.create_all()
        test_set = MtgCardSetModel()
        test_set.name = "TEST SET"
        test_set.code = "TST"
        test_set.block = "Testing Block"
        test_set.release_date = datetime.datetime(year=1979, month=1, day=1)
        test_set.insert()

        other_test_set = MtgCardSetModel()
        other_test_set.name = "TEST SET 2"
        other_test_set.code = "TS2"
        other_test_set.block = "Testing Block"
        other_test_set.release_date = datetime.datetime(year=1979, month=1, day=1)
        other_test_set.insert()

        test_card = MtgCardModel()
        test_card.name = "Test Card 1"
        test_card.multiverse_id = 150
        test_card.set_id = test_set.id
        test_card.insert()

        second_test_card = MtgCardModel()
        second_test_card.name = "Test Card 1"
        second_test_card.multiverse_id = 250
        second_test_card.set_id = other_test_set.id
        second_test_card.insert()
        db.Session.commit()


    def test_api_get_cards_from_props_with_set(self):
        cards = get_cards_from_properties(name="Test Card 1", set="TST")
        self.assertEqual(len(cards), 1)
        card = cards[0]
        self.assertEqual(card.name, "Test Card 1")

    def test_api_get_cards_from_props_no_set(self):
        cards = get_cards_from_properties(name="Test Card 1")
        self.assertEqual(len(cards), 2)
        set_codes = [c.set.code for c in cards]
        self.assertTrue("TST" in set_codes)
        self.assertTrue("TS2" in set_codes)

    def test_api_get_random_card(self):
        card = get_random_card()
        self.assertTrue(card)


class APISetTestCase(DbUnitTestBase):

    def setUp(self):
        db.make_tables()
        self.load_data()

    def tearDown(self):
        db.drop_tables()

    def load_data(self):
        card_set = MtgCardSetModel()
        card_set.name = "Test Set"
        card_set.code = "TST"
        card_set.insert()
        db.Session.commit()

    def test_api_get_set(self):
        s = get_set("TST")
        self.assertTrue(s)
