import unittest
import mock
from tests import app
from tests.unit_tests.base import DbUnitTestBase
from mtg_api.models.magic import MtgCardModel, MtgCardSetModel
from mtg_api.db import db_instance as db
import datetime
from mtg_api.models.magic import ManaCostModel, MtgCardModel, MtgCardSetModel
from mtg_api.models.magic import ManaSymbolModel, ManaTypeModel


class ManaCostModelTestCase(DbUnitTestBase):

    def setUp(self):
        db.make_tables()
        self.load_data()

    def tearDown(self):
        db.drop_tables()

    def load_data(self):
        ManaTypeModel.populate()

        test_set = MtgCardSetModel()
        test_set.name = "TEST SET"
        test_set.code = "TST"
        db.Session.add(test_set)

        self.test_card = MtgCardModel()
        self.test_card.set = test_set
        self.test_card.name = "TEST NAME"
        self.test_card.mana_cost = ManaCostModel()
        db.Session.add(self.test_card)
        db.Session.commit()

    def test_normal_mana_cost_string(self):
        g_mana = ManaSymbolModel()
        g_mana.value = 2
        mt = ManaTypeModel()
        mt.mana_type = "generic"
        g_mana.mana_types.append(mt)

        u_mana = ManaSymbolModel()
        mt2 = ManaTypeModel()
        mt2.mana_type = "blue"
        u_mana.mana_types.append(mt2)

        self.test_card.mana_cost.mana_symbols.extend((g_mana, u_mana))
        cost_str = self.test_card.mana_cost.get_symbol_string()
        self.assertEqual(cost_str, "{2}{U}")

    def test_chromatic_mana_cost_string(self):
        for mt in ("green", "blue", "black", "white", "red"):
            s = ManaSymbolModel()
            mana_type = ManaTypeModel()
            mana_type.mana_type = mt
            s.mana_types.append(mana_type)
            self.test_card.mana_cost.mana_symbols.append(s)
        cost_str = self.test_card.mana_cost.get_symbol_string()
        self.assertEqual(cost_str, "{W}{U}{B}{R}{G}")
