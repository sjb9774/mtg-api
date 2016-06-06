from mtg_api.app import app
from flask import render_template, jsonify, request, send_from_directory, abort
from flask import redirect
from mtg_api.models.magic import MtgCardModel, MtgCardSetModel
from mtg_api.models.users import User
from mtg_api.models.sessions import Session
from mtg_api.utils.search import get_card_suggestions
from mtg_api.utils.users import login, get_active_user, hash_password, create_user
from mtg_api.utils.views import api_route, custom_render, ApiMapper
from mtg_api.api import get_cards_from_properties, get_random_card, get_set
from jinja2 import TemplateNotFound
import json
import db

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
        return jsonify({'cards':[card.dictify() for card in cards]})

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
