#!/usr/bin/env python
from mtg_api.mtg.magic import MtgCardSet, MtgCard, ManaSymbol
from mtg_api.mtg.colors import Color
from mtg_api.mtg import TYPES, ALL_COLOR_COMBINATIONS, COLORS
from mtg_api.models.magic import MtgCardSetModel, MtgCardModel, ManaCostModel, ManaSymbolModel
from mtg_api.models.magic import ManaTypeModel
from mtg_api.models.magic import TypeModel, SubtypeModel, XCardType, XCardSubtype, SupertypeModel
from mtg_api.models.magic import RulingModel, XCardRuling, FormatModel, XCardFormat
from mtg_api.DATA.card_data_handler import get_card_data
from mtg_api.DATA.parsing import parse_format, parse_card, parse_mana_symbol, parse_mana_cost
from mtg_api.DATA.parsing import parse_power_toughness, parse_types, parse_subtypes, parse_ruling
from mtg_api.my_database import MyDatabase
from mtg_api.db import db_instance as db
from logging import Logger
from collections import OrderedDict
import time
import re
from mtg_api.config import config

def do_data_process(*sets):
    print "Beginning card process..."
    CARD_DATA = get_card_data(*sets)
    stime = time.time()
    mtg = {}
    all_data = OrderedDict()
    mana_costs = []
    types = set()
    xtypes = []
    formats, xformats = set(), []
    rulings, xrulings = [], []

    mana_symbol_dict = {}
    card_set_prop_map = {
        'releaseDate': 'release_date',
        'type': 'set_type'
    }

    card_prop_map = {
        'cmc': 'converted_mana_cost',
        'manaCost': 'mana_cost',
        'multiverseid': 'multiverse_id',
        'subtypes': 'subtype',
        'types': 'type',
        'names': 'transform',
    }
    transform_map = {}
    mana_cost_regx_str = r'\s*(\{[\w\d/]+\})\s*'
    mana_cost_regx = re.compile(mana_cost_regx_str)
    set_time = time.time()
    total_cards = 0
    total_sets = 0
    for set_code, set_data in CARD_DATA:
        total_sets += 1
        print 'Processing set {set_code}...'.format(set_code=set_code)
        mtg[set_code] = {'set': None, 'cards': []}
        mtg[set_code]['set'] = make_instance(MtgCardSetModel, card_set_prop_map, **set_data)
        for card_dict in set_data['cards']:
            total_cards += 1
            # flags for logging
            cl_hybrid = False
            phy = False
            mana_symbols = []
            if 'manaCost' not in card_dict:
                mana_cost = ManaCostModel()
                symbol = ManaSymbolModel.get_mana_symbol([ManaSymbol.GENERIC], value=0)
                mana_symbol_id = symbol.id
                mana_cost.mana_symbol_id = mana_symbol_id
            else:
                raw_mana_cost = card_dict.pop('manaCost')
                for token in mana_cost_regx.findall(raw_mana_cost):
                    symbol = parse_mana_symbol(token)
                    mana_symbols.append(symbol)

            raw_power = card_dict.pop('power', None)
            raw_toughness = card_dict.pop("toughness", None)
            power = parse_power_toughness(raw_power)
            toughness = parse_power_toughness(raw_toughness)

            card = make_instance(MtgCardModel,
                                 card_prop_map,
                                 toughness=toughness,
                                 power=power,
                                 raw_power=raw_power,
                                 raw_toughness=raw_toughness,
                                 set_id=mtg[set_code]['set'].id,
                                 **card_dict)

            if card and mana_symbols:
                mana_cost = ManaCostModel.create(card, mana_symbols)

            for ruling_data in card_dict.get('rulings', []):
                r = parse_ruling(ruling_data)
                card.rulings.append(r)

            for format_dict in card_dict.get('legalities', []):
                format_name, format_legality = format_dict["format"], format_dict["legality"]
                if format_legality.lower() == 'legal':
                    format_model = FormatModel.get_or_make(name=format_name)
                    # TODO: RELATE CARD NAME AND FORMAT ID IN XCARDFORMAT, LIKEWISE FOR RULINGS
                    card.formats.append(format_model)

            # types and mana costs are dissociated from the actual card now, so process after
            for type_tuple in (('types', TypeModel), ('subtypes', SubtypeModel), ('supertypes', SupertypeModel)):
                type_str, type_cls = type_tuple
                if card_dict.get(type_str):
                    lowercase_types = [t.lower() for t in card_dict.pop(type_str)]
                    for i, t in enumerate(lowercase_types):
                        # create/make the type instance
                        instance = type_cls.get_or_make(name=t)
                        getattr(card, type_str).append(instance)

            # it's a transform card
            if card_dict.get('layout') == 'double-faced':
                # if the other side of this card has been found already, there will be
                # an entry in transform map mapping this card's name to the model of the other side
                transform = transform_map.get(card.name)
                if transform:
                    card.transform_multiverse_id = transform.multiverse_id
                # if the other side has not been found, make an entry in transform_map, the cards
                # will be linked once the other card is found
                else:
                    transform_name = [name for name in card_dict['names'] if name != card_dict['name']][0]
                    transform_map[transform_name] = card
            mtg[set_code]["set"].cards.append(card)
            mtg[set_code]['cards'].append(card)
        print 'Set completed, took {duration} seconds to process'.format(duration=time.time()-set_time)
        set_time = time.time()
        mtg[set_code]["set"].add()
    total_time = time.time() - stime
    print 'Processing done, total time {total_time} seconds to process {total_sets} sets and {total_cards} cards.'.format(**locals())
    return mtg, mana_costs, list(types), xtypes, rulings, xrulings, list(formats), xformats

def make_instance(cls, property_map, **kwargs):
    new_dict = {}
    for kw, arg in kwargs.iteritems():
        # if the name is mapped to something new in the property_map
        # and the mapped name is a valid attribute in MtgCardSet
        if property_map.get(kw) and hasattr(cls, property_map[kw]):
            new_dict[property_map[kw]] = arg
        # if the kwarg passed is an attribute of cls but not in the property_map,
        # go ahead and set it, so we don't have to specify map instances where the
        # property name doesn't change (eg, no "name": "name", "code": "code"...)
        elif hasattr(cls, kw):
            new_dict[kw] = arg
    instance = cls(**new_dict)
    return instance

def mysql_dump(data, commit_interval=500):
    start = time.time()
    commit_interval = commit_interval
    db.Session.commit()
    print 'Done!'

def verbose_commit(insertables, name, commit_interval=500):
    start = time.time()
    total = len(insertables)
    for i, t in enumerate(insertables, start=1):
        t.insert(commit=False)
        if i != 0 and i % commit_interval == 0:
            print "{current}/{total} {name} committed.".format(current=i, total=total, name=name)
            db.Session.commit()
    db.Session.commit()
    print '{total} {name} committed, took {time} seconds.'.format(time=time.time()-start,
                                                                  name=name,
                                                                  total=total)

def prep_mana_symbols():
    ManaTypeModel.populate()
    db.Session.commit()

def gen_print(g, start_msg='Starting...', done_msg='Done!'):
    print start_msg
    problem_size = g.next()
    problem_progress = g.next()
    while problem_progress < problem_size:
        print '\r{prog}/{total}'.format(prog=problem_progress, total=problem_size),
        problem_progress = g.next()
    print done_msg

def do_all(*sets):
    start = time.time()
    try:
        prep_mana_symbols()
        mtg_data = do_data_process(*sets)
        mysql_dump(mtg_data)
    except KeyboardInterrupt:
        print 'Rolling back before exit!'
        db.Session.rollback()
        raise
    print 'Total processing time: {time}'.format(time=time.time()-start)

if __name__ == "__main__":
    do_all()
