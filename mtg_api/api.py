from mtg_api.models.magic import MtgCardModel, MtgCardSetModel
from mtg_api.models.users import User
from mtg_api.models.sessions import Session
from mtg_api.utils.search import get_card_suggestions
import db

def get_cards_from_properties(**props):
    cards = MtgCardModel.filter_by(**filtered_args)
    if props.get('set'):
        cards = cards.join(MtgCardSetModel).filter_by(code=props.get('set')).all()
    return cards

def get_random_card():
    import random
    multiverse_ids = db.Session.query(MtgCardModel.multiverse_id)\
                               .filter(MtgCardModel.multiverse_id != None)\
                               .all()
    random_id = multiverse_ids[random.randint(0, len(multiverse_ids))][0]
    random_card = MtgCardModel.filter_by(multiverse_id=random_id).first()
    return random_card
