from sqlalchemy import Table, Column, VARCHAR, Integer, Boolean, ForeignKey, Enum, Date, Float
from sqlalchemy.orm import  relationship
from mtg_api.db import db_instance as db, IdMixin, Base, DefaultMixin, id_length
from mtg_api.mtg.magic import MtgCard, MtgCardSet, ManaSymbol, Type, Subtype
from mtg_api.mtg.colors import Color
from mtg_api.mtg import ALL_COLOR_COMBINATIONS, TYPES, SET_TYPES


class MtgCardModel(IdMixin, Base, DefaultMixin, MtgCard):
    __tablename__ = 'cards'

    __fields__ = MtgCard.__fields__ + ['raw_power', 'raw_toughness']

    multiverse_id = Column(Integer)
    name = Column(VARCHAR(200), nullable=False, index=True) # must create index for foreign keys that reference this
    set_id = Column(VARCHAR(id_length), ForeignKey('sets.id'))
    colors = Column(Enum(*['/'.join(c) for c in ALL_COLOR_COMBINATIONS]))

    power = Column(Float)
    toughness = Column(Float)
    raw_power = Column(VARCHAR(25))
    raw_toughness = Column(VARCHAR(25))
    loyalty = Column(Integer)
    foil = Column(Enum('foil', 'normal', 'special'))
    converted_mana_cost = Column(Integer)
    # can we use a foreign key or will the constraint always fail due to circular referencing?
        # ie Ludevic's Subject.transform_id = 'xxxx' = Ludevic's Abomination.transform_id
    transform_multiverse_id = Column(VARCHAR(id_length))
    rarity = Column(Enum("common", "uncommon", "rare", "special", "mythic rare", "other", "promo", "basic land"))
    text = Column(VARCHAR(1000))
    flavor = Column(VARCHAR(1000))

    def __init__(self, **kwargs):
        power = kwargs.get('power')
        toughness = kwargs.get('toughness')
        for pt in ('power', 'toughness'):
            stat = kwargs.pop(pt, None)
            if type(stat) == str or type(stat) == unicode:
                value = None
                if stat.lower() in ('*', 'x'):
                    value = 0
                elif stat.isdigit():
                    value = int(stat)

                if pt == 'power':
                    power = value
                else:
                    toughness = value
        MtgCard.__init__(self, power=power, toughness=toughness, **kwargs)
        IdMixin.__init__(self)

    @property
    def converted_mana_cost(self):
        mana_costs = ManaCostModel.filter_by(card_id=self.id).all()
        cmc = 0
        for mc in mana_costs:
            cmc += mc.count * mc.mana_symbol.value
        return int(cmc)

    @property
    def mana_cost(self):
        mana_costs = db.Session.query(ManaSymbolModel, ManaCostModel.count)\
                               .join(ManaCostModel)\
                               .filter_by(card_id=self.id)\
                               .all()
        return [(''.join([color.abbreviation for color in symbol.colors]), count) for symbol, count in mana_costs]


    @property
    def transform_card(self):
        if self.transform_multiverse_id:
            return MtgCardModel.filter(MtgCardModel.multiverse_id==self.transform_multiverse_id).first()
        elif self.multiverse_id:
            return MtgCardModel.filter(MtgCardModel.transform_multiverse_id==self.multiverse_id).first()
        else:
            return None

    @property
    def all_sets(self):
        sets = MtgCardSetModel.join(MtgCardModel, MtgCardModel.set_id == MtgCardSetModel.id)\
                              .filter(MtgCardModel.name==self.name)\
                              .filter(MtgCardModel.multiverse_id != None)\
                              .order_by(MtgCardSetModel.release_date)\
                              .all()
        return sets

    @property
    def types(self):
        return [r for (r,) in db.Session.query(TypeModel.name)\
                                        .join(XCardType)\
                                        .filter(XCardType.card_id==self.id)\
                                        .all()]

    @property
    def subtypes(self):
        return [r for (r,) in db.Session.query(SubtypeModel.name)\
                                        .join(XCardSubtype)\
                                        .filter(XCardSubtype.card_id==self.id)\
                                        .all()]

    @property
    def image_url(self):
        return "http://gatherer.wizards.com/Handlers/Image.ashx?multiverseid={}&type=card".format(self.multiverse_id)

    def other_arts(self):
        return MtgCardModel.filter(MtgCardModel.set_id == self.set_id)\
                           .filter(MtgCardModel.name == self.name)\
                           .filter(MtgCardModel.multiverse_id != None)\
                           .filter(MtgCardModel.multiverse_id != self.multiverse_id)\
                           .all()

    def dictify(self):
        data = {
                    'multiverseId': self.multiverse_id,
                    'name': self.name,
                    'rulesText': self.text,
                    'flavorText': self.flavor,
                    'set': self.set.code,
                    'power': self.raw_power,
                    'toughness': self.raw_toughness,
                    'transformMultiverseId': self.transform_multiverse_id,
                    'loyalty': self.loyalty,
                    'colors': self.colors,
                    'types': self.types,
                    'subtypes': self.subtypes,
                    'cmc': self.converted_mana_cost,
                    'otherArts': [{"multiverseId": c.multiverse_id} for c in self.other_arts()],
                    'manaCost': {''.join(abbr): num for abbr, num in self.mana_cost},
                    'imageUrl': self.image_url if self.multiverse_id else '',
                    #'imageUrl': '/image?name={name}&set={set_code}'.format(name=self.name, set_code=self.set.code),
                    'allSets': [s.code for s in self.all_sets]
                }
        return {k:v for k, v in data.iteritems() if v}

class MtgCardSetModel(Base, DefaultMixin, IdMixin, MtgCardSet):

    __tablename__ = 'sets'
    name = Column(VARCHAR(200))
    code = Column(VARCHAR(10))
    block = Column(VARCHAR(200))
    release_date = Column(Date)
    set_type = Column(Enum(*SET_TYPES))
    cards = relationship('MtgCardModel', backref='set')

    def __init__(self, **kwargs):
        MtgCardSet.__init__(self, **kwargs)
        IdMixin.__init__(self)


from sqlalchemy import event
class ManaSymbolModel(IdMixin, Base, DefaultMixin, ManaSymbol):

    __tablename__ = 'mana_symbols'

    r = Column(Boolean, default=False)
    u = Column(Boolean, default=False)
    b = Column(Boolean, default=False)
    g = Column(Boolean, default=False)
    w = Column(Boolean, default=False)
    c = Column(Boolean, default=False)
    x = Column(Boolean, default=False)
    value = Column(Float, default=1)

    label = Column(VARCHAR(10))

    phyrexian = Column(Boolean, default=False)

    def __init__(self, *args, **kwargs):
        IdMixin.__init__(self)
        ManaSymbol.__init__(self, **kwargs)


# a couple of functions to bridge the gap between the database representation and the basic representation
@event.listens_for(ManaSymbolModel, 'load')
def set_colors(target, context):
    colors = ('b', 'g', 'r', 'u', 'w', 'c')
    mana_symbol = target
    mana_symbol.colors = []
    for color in colors:
        if getattr(mana_symbol, color):
            mana_symbol.colors.append(Color(color))

@event.listens_for(ManaSymbolModel.r, 'set')
@event.listens_for(ManaSymbolModel.u, 'set')
@event.listens_for(ManaSymbolModel.b, 'set')
@event.listens_for(ManaSymbolModel.w, 'set')
@event.listens_for(ManaSymbolModel.g, 'set')
def refresh_colors(target, value, old_value, initiator):
    if value not in (True, False, None):
        raise ValueError('Colors can only be set to True, False, or None for a ManaSymbolModel')
    else:
        colors = ('b', 'g', 'r', 'u', 'w', 'c')
        mana_symbol = target

        mana_symbol.colors = [Color(abbr) for abbr in colors if getattr(mana_symbol, abbr) and abbr != initiator.key]
        if value:
            mana_symbol.colors.append(Color(initiator.key))


class ManaCostModel(IdMixin, Base, DefaultMixin):

    __tablename__ = 'mana_costs'

    card_id = Column(VARCHAR(id_length), ForeignKey('cards.id'))
    mana_symbol_id = Column(VARCHAR(id_length), ForeignKey('mana_symbols.id'))
    count = Column(Integer)
    mana_symbol = relationship('ManaSymbolModel')

class FormatModel(IdMixin, Base, DefaultMixin):

    __tablename__ = 'formats'

    name = Column(VARCHAR(200))

class RulingModel(IdMixin, Base, DefaultMixin):

    __tablename__ = 'rulings'

    date = Column(Date)
    ruling = Column(VARCHAR(5000))


class XCardRuling(IdMixin, Base, DefaultMixin):

    __tablename__ = 'x_card_rulings'

    card_name = Column(VARCHAR(200), ForeignKey('cards.name'), nullable=False)
    ruling_id = Column(VARCHAR(id_length), ForeignKey('rulings.id'), nullable=False)

class XCardFormat(IdMixin, Base, DefaultMixin):

    __tablename__ = 'x_card_formats'

    card_name = Column(VARCHAR(200), ForeignKey('cards.name'), nullable=False)
    format_id = Column(VARCHAR(id_length), ForeignKey('formats.id'), nullable=False)

class TypeModel(IdMixin, Base, DefaultMixin, Type):

    __tablename__ = 'types'

    name = Column(VARCHAR(200))


class SubtypeModel(IdMixin, Base, DefaultMixin, Subtype):

    __tablename__ = 'subtypes'

    name = Column(VARCHAR(200))


class XCardType(IdMixin, Base, DefaultMixin):

    __tablename__ = 'x_card_types'

    card_id = Column(VARCHAR(id_length), ForeignKey('cards.id'))
    type_id = Column(VARCHAR(id_length), ForeignKey('types.id'))
    priority = Column(Integer)


class XCardSubtype(IdMixin, Base, DefaultMixin):

    __tablename__ = 'x_card_subtypes'

    card_id = Column(VARCHAR(id_length), ForeignKey('cards.id'))
    subtype_id = Column(VARCHAR(id_length), ForeignKey('subtypes.id'))
    priority = Column(Integer)
