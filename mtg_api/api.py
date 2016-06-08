from mtg_api.models.magic import MtgCardModel, MtgCardSetModel
from mtg_api.models.users import User
from mtg_api.models.sessions import Session
from mtg_api.utils.search import get_card_suggestions
from mtg_api.db import db_instance as db

def get_cards_from_properties(**props):
    card_set = props.pop("set", None)
    cards = MtgCardModel.filter_by(**props)
    if card_set:
        cards = cards.join(MtgCardSetModel).filter_by(code=card_set).all()
    else:
        cards = cards.all()
    return cards

def get_random_card():
    import random
    multiverse_ids = db.Session.query(MtgCardModel.multiverse_id)\
                               .filter(MtgCardModel.multiverse_id != None)\
                               .all()
    random_id = multiverse_ids[random.randint(0, len(multiverse_ids) - 1)][0]
    random_card = MtgCardModel.filter_by(multiverse_id=random_id).first()
    return random_card

def get_set(set_code):
    card_set = MtgCardSetModel.filter(MtgCardSetModel.code == set_code).one()
    return card_set
