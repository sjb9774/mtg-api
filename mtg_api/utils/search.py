from mtg_api.models.magic import MtgCardModel, MtgCardSetModel
from mtg_api import db

def get_card_suggestions(name):
    potential = db.Session.query(MtgCardModel)\
                          .join(MtgCardSetModel)\
                          .filter(MtgCardModel.name.op('regexp')(name))\
                          .all()
    suggestions = {}
    for card in potential:
        if not suggestions.get(card.name) or (suggestions.get(card.name) and suggestions.get(card.name).set.release_date < card.set.release_date):
            suggestions[card.name] = card
    return sorted(suggestions.values(), cmp=lambda x, y: 1 if x.name > y.name else -
    1)
