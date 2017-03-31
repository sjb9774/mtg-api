from mtg_api.app import app
from flask import render_template, jsonify, request, send_from_directory, abort
from flask import redirect
from sqlalchemy import func
from mtg_api.models.magic import MtgCardModel, MtgCardSetModel
from mtg_api.utils.search import get_card_suggestions
from mtg_api.utils.views import api_route, ApiMapper
from mtg_api.api import get_cards_from_properties, get_random_card, get_set
from jinja2 import TemplateNotFound
import json
from mtg_api.db import db_instance as db
import re

@api_route('/api/card', methods=['GET'])
def api_get_card(get_args):
    if not get_args:
        # TODO: Return a nice page detailing how to use the api
        return 'Needs some arguments!'
    else:
        filtered_args = {kw: get_args[kw] for kw in get_args if kw in MtgCardModel.__fields__}
        card_set = get_args.get('set')
        if card_set:
            filtered_args['set'] = card_set
        cards = get_cards_from_properties(**filtered_args)
        r = {'cards':[card.dictify() for card in cards]}
        return jsonify(r)

@api_route('/api/card/search', methods=['GET'])
def api_search_cards(get_args):
    criteria = ["types", "subtypes", "color", "name", "set", "artist", "rarity", "oracle", "flavor"]
    search_dict = {k: v for k, v in get_args.iteritems() if k in criteria}
    if not search_dict:
        return jsonify({"success": False, "message": "No query specified"})
    else:
        operators = {"in": "in_", "and": "and_", "or": "or_", "not": "__neg__", "=": "__eq__"}
        expression_rgx = re.compile(r"(\w+)\(([\w\d]+)\)")
        q = db.Session.query(MtgCardModel)
        for criterion, value in search_dict.iteritems():
            attr = getattr(MtgCardModel, criterion)
            comparator = getattr(attr, operators[parse_operator(value)])
            q = q.filter(comparator())

@api_route('/api/card/random', methods=['GET'])
def api_get_random_card(get_args):
    random_card = get_random_card()
    return jsonify({'cards': [random_card.dictify()]})

@api_route('/api/set', methods=['GET'])
def api_get_card_set(get_args):
    set_code = get_args.get('code') or get_args.get('setCode')
    card_set = get_set(set_code)
    results = card_set.dictify()
    results['cards'] = [{'url': ApiMapper.api_get_card(c, ['multiverse_id']), 'name': c.name} for c in card_set.cards]
    return jsonify(results)

@api_route('/api/find_cards', methods=['GET'])
def api_find_cards(get_args):
    name_fragment = get_args.get('name')
    cards = db.Session.query(MtgCardModel)\
                           .join(MtgCardSetModel)\
                           .filter(func.lower(MtgCardModel.name).like('%' + name_fragment.lower() + '%'))\
                           .order_by(MtgCardModel.name.asc())\
                           .all()
    return jsonify({'cards': [c.dictify() for c in cards], 'quantity': len(cards)})
