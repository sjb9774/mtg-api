from mtg_api import app
from flask import render_template, jsonify, request, send_from_directory, abort
from flask import redirect
from mtg_api.models.magic import MtgCardModel, MtgCardSetModel
from mtg_api.models.users import User
from mtg_api.models.sessions import Session
from mtg_api.utils.search import get_card_suggestions
from mtg_api.utils.users import login, get_active_user, hash_password, create_user
from mtg_api.utils.views import custom_route, custom_render
from jinja2 import TemplateNotFound
import json
import db

@custom_route('/api/card', methods=['GET'])
def api_get_card(get_args):
    if not get_args:
        # TODO: Return a nice page detailing how to use the api
        return 'Needs some arguments!'
    else:
        filtered_args = {kw: get_args[kw] for kw in get_args if kw in MtgCardModel.__fields__}
        cards = MtgCardModel.filter_by(**filtered_args)
        if get_args.get('set'):
            cards = cards.join(MtgCardSetModel).filter_by(code=get_args.get('set')).all()
        return jsonify({'cards':[card.dictify() for card in cards]})

@custom_route('/api/deck/history', methods=['GET'])
def api_get_deck_history(get_args):
    deck_id = get_args.get('uuid')
    if deck_id:
        deck = Deck.get(deck_id)
        def recursive_deck_map(deck_id):
            results = []
            more_decks = db.Session.query(Deck)\
                                   .filter(Deck.root_deck_id==deck_id)\
                                   .filter(Deck.id != deck_id)\
                                   .order_by(Deck.deck_index.desc())\
                                   .all()
            if more_decks:
                for deck in more_decks:
                    results.append(deck.dictify())
                    results[-1]['children'] = recursive_deck_map(deck.id)
            return results

        results = {
            'decks': {}
        }
        results['decks'] = deck.dictify()
        results['decks']['children'] = recursive_deck_map(deck.id)
        return jsonify(results)

@custom_route('/api/deck', methods=['GET'])
def api_get_deck(get_args):
    deck_name = get_args.get('name')
    username = get_args.get('username')
    if deck_name and username:
        deck = db.Session.query(Deck)\
                         .join(User)\
                         .filter(User.username==username)\
                         .filter(Deck.name==deck_name)\
                         .one()
        if deck:
            return jsonify({'deck': deck.dictify(), 'success': True})
        else:
            return jsonify({'success': False, 'message': 'No deck found'})
    else:
        return jsonify({'success': False, 'message': 'No args given'})

@custom_route('/api/deck/fork', methods=['POST'])
def api_fork_deck(post_args):
    deck_id = post_args.get('deckId')
    deck = Deck.get(deck_id)
    new_name = post_args.get('deckName') or deck.name
    is_current = post_args.get('isCurrent')
    if deck:
        new_deck, new_xcards = create_forked_deck(deck, new_name=new_name, is_current=is_current)
        new_deck.insert()
        [xcard.insert() for xcard in new_xcards]
        db.Session.commit()
        return jsonify({'success': True, 'deckUrl': '/view/decks/{username}/{deck_name}'.format(username=get_active_user().username, deck_name=new_deck.name)})
    else:
        return jsonify({'success': False, 'message': "Couldn't fork deck"})
