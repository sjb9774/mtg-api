#!/usr/bin/env python
from mtg_api.mtg.magic import MtgCardSet, MtgCard, ManaSymbol
from mtg_api.mtg.colors import Color
from mtg_api.mtg import TYPES, ALL_COLOR_COMBINATIONS, COLORS
from mtg_api.models.magic import MtgCardSetModel, MtgCardModel, ManaCostModel, ManaSymbolModel
from mtg_api.models.magic import TypeModel, SubtypeModel, XCardType, XCardSubtype
from mtg_api.models.magic import RulingModel, XCardRuling, FormatModel, XCardFormat
from mtg_api.DATA.card_data_handler import get_card_data
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
    mana_symbols = ManaSymbolModel.all()
    if not mana_symbols:
        prep_mana_symbols()
        mana_symbols = ManaSymbolModel.all()
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
    mana_cost_regx_str = r'\s*\{([\w\d/]+)\}\s*'
    mana_cost_regx = re.compile(mana_cost_regx_str)
    set_time = time.time()
    total_cards = 0
    total_sets = 0
    for set_code, set_data in CARD_DATA:
        total_sets += 1
        print 'Processing set {set_code} #{num}...'.format(set_code=set_code, num=total_sets)
        mtg[set_code] = {'set': None, 'cards': []}
        mtg[set_code]['set'] = make_instance(MtgCardSetModel, card_set_prop_map, **set_data)
        for card_dict in set_data['cards']:
            total_cards += 1
            # flags for logging
            cl_hybrid = False
            phy = False

            cost = {}
            if 'manaCost' not in card_dict:
                # defaults all costs to zero
                mana_cost = ManaCostModel()
                symbol = mana_symbol_dict.setdefault('c', ManaSymbolModel.get_or_make(x=False,
                                                                                      phyrexian=False,
                                                                                      **{k:(False if k != 'c' else True) for k in COLORS}))
                mana_cost.count = 0
                mana_symbol_id = symbol.id
            else:
                raw_mana_cost = card_dict.pop('manaCost')
                # token = {4} or {g/w} or {r} etc...
                for token in mana_cost_regx.findall(raw_mana_cost):
                    if token.isdigit():
                        symbol = mana_symbol_dict.setdefault('c', ManaSymbolModel.get_or_make(x=False,
                                                                                              phyrexian=False,
                                                                                              **{k:(False if k != 'c' else True) for k in COLORS}))
                        current = cost.setdefault(symbol, 0)
                        cost[symbol] = current + int(token)
                    elif token.lower() in ('x', 'y', 'z'): # Ultimate Nightmare of Wizard's of the Coast Customer Service :\
                        symbol = mana_symbol_dict.setdefault(ManaSymbol(x=True, label=token.lower()).symbol(),
                                                             ManaSymbolModel.get_or_make(x=True, label=token.lower()))
                        current = cost.setdefault(symbol, 0)
                        cost[symbol] += 1
                    else:
                        parts = token.split('/')
                        is_phy = ('P' in parts) or ('p' in parts)
                        colors = [c.lower() for c in parts if c.lower() != 'p' and not c.isdigit()]
                        colorless_pieces = [int(num) for num in parts if num.isdigit()]
                        if colorless_pieces:
                            cl_hybrid = True
                            value = colorless_pieces[0]
                            colors.append('c')
                        elif [half_cost for half_cost in parts if half_cost.lower().find('h') != -1]:
                            # if any of these "colors" have 'h' in them, they're a half-mana from Unhinged :(
                            value = .5
                            colors = [color[-1] for color in colors]
                        else:
                            value = 1
                        if is_phy:
                            phy = True
                        symbol = mana_symbol_dict.setdefault(ManaSymbol(colors=colors, phyrexian=is_phy, value=value).symbol(),
                                                             ManaSymbolModel.get_or_make(phyrexian=is_phy, value=value, **{c.lower(): (True if c in colors else False) for c in COLORS}))
                        current = cost.setdefault(symbol, 0)
                        cost[symbol] += symbol.value
            if cl_hybrid:
                print '{name} ({mid}) has hybrid colorless/colored mana! Weird!'.format(name=card_dict['name'], mid=card_dict.get('multiverseid'))
            if phy:
                print '{name} ({mid}) is phyrexian!'.format(name=card_dict['name'], mid=card_dict.get('multiverseid'))

            if not card_dict.get('colors'):
                colors = None
            else:
                colors = [Color(c) for c in card_dict.pop('colors')]
                colors = sorted([c.abbreviation for c in colors])
                colors = '/'.join(colors)

            try:
                raw_power = card_dict.pop('power')
                power = float(raw_power)
            except ValueError:
                power = 0
            except KeyError:
                raw_power = None
                power = None
            try:
                raw_toughness = card_dict.pop('toughness')
                toughness = float(raw_toughness)
            except ValueError:
                toughness = 0
            except KeyError:
                raw_toughness = None
                toughness = None

            card = make_instance(MtgCardModel,
                                 card_prop_map,
                                 toughness=toughness,
                                 power=power,
                                 raw_power=raw_power,
                                 raw_toughness=raw_toughness,
                                 colors=colors,
                                 set_id=mtg[set_code]['set'].id,
                                 **card_dict)

            for ruling_data in card_dict.get('rulings', []):
                r = RulingModel()
                r.date = ruling_data['date']
                r.ruling = ruling_data['text']
                xr = XCardRuling()
                xr.card_name = card.name
                xr.ruling_id = r.id
                rulings.append(r)
                xrulings.append(xr)


            for format_name, format_legality in card_dict.get('legalities', {}).iteritems():
                if format_legality.lower() == 'legal':
                    format_model = FormatModel.get_or_make(name=format_name)
                    # TODO: RELATE CARD NAME AND FORMAT ID IN XCARDFORMAT, LIKEWISE FOR RULINGS
                    xformat = XCardFormat()
                    xformat.format_id = format_model.id
                    xformat.card_name = card.name
                    formats.add(format_model)
                    xformats.append(xformat)

            # types and mana costs are dissociated from the actual card now, so process after
            for type_type in (('types', TypeModel, XCardType), ('subtypes', SubtypeModel, XCardSubtype)):
                type_str, type_cls, x_cls = type_type
                if card_dict.get(type_str):
                    lowercase_types = [t.lower() for t in card_dict.pop(type_str)]
                    for i, t in enumerate(lowercase_types):
                        # create/make the type instance
                        instance = type_cls.get_or_make(name=t)
                        x_thing = x_cls()
                        x_thing.card_id = card.id
                        x_thing.priority = i
                        if type_str == 'types':
                            x_thing.type_id = instance.id
                        else:
                            x_thing.subtype_id = instance.id
                        types.add(instance)
                        xtypes.append(x_thing)


            for symbol, count in cost.iteritems():
                mana_cost = ManaCostModel()
                mana_cost.count = count
                mana_cost.mana_symbol_id = symbol.id
                mana_cost.card_id = card.id
                mana_costs.append(mana_cost)

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
            mtg[set_code]['cards'].append(card)
        print 'Set completed, took {duration} seconds to process'.format(duration=time.time()-set_time)
        set_time = time.time()
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

def detupled_list(lst):
    return [tup[0] for tup in lst]

def mysql_dump(data, commit_interval=500):
    start = time.time()
    commit_interval = commit_interval
    card_map, costs, types, xtypes, rulings, xrulings, formats, xformats = data
    print 'Setting set ids to cards...'
    sets, cards = [], []
    for set_code, info_dict in card_map.iteritems():
        sets.append(info_dict['set'])
        for card in info_dict['cards']:
            card.set_id = info_dict['set'].id
            cards.append(card)
    print 'Done!'
    for insertables in (sets, cards, costs, types, xtypes, rulings, xrulings, formats, xformats):
        if insertables:
            verbose_commit(insertables, insertables[0].__tablename__, commit_interval=commit_interval)
    print 'Total commit time: {time} seconds.'.format(time=time.time()-start)

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
    if ManaSymbolModel.all():
        return
    for cc in [comb for comb in ALL_COLOR_COMBINATIONS if len(comb) <= 2]:
        for b in (True, False):
            ms = ManaSymbolModel()
            ms.phyrexian = b
            for c in cc:
                setattr(ms, c, True)
            ms.insert(commit=False)

    colorless = ManaSymbolModel()
    colorless.insert(commit=False)

    for label in ('x', 'y', 'z'):
        x_cost = ManaSymbolModel()
        x_cost.x = True
        x_cost.value = 0
        x_cost.label = label
        x_cost.insert(commit=False)
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
