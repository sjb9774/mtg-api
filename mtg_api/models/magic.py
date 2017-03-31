from sqlalchemy import Table, Column, VARCHAR, Integer, Boolean, ForeignKey, Enum, Date, Float
from sqlalchemy.orm import  relationship
from mtg_api.db import db_instance as db, IdMixin, Base, DefaultMixin, id_length
from mtg_api.mtg.magic import MtgCard, MtgCardSet, ManaSymbol, Type, Subtype
from mtg_api.mtg.colors import Color
from mtg_api.mtg import ALL_COLOR_COMBINATIONS, TYPES, SET_TYPES

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


class SupertypeModel(IdMixin, Base, DefaultMixin):

    all_supertypes = ["basic", "elite", "legendary", "ongoing", "world", "snow"]

    __tablename__ = 'supertypes'

    name = Column(Enum(*all_supertypes))


class XCardSupertype(IdMixin, Base, DefaultMixin):

    __tablename__ = 'x_card_supertypes'

    card_id = Column(VARCHAR(id_length), ForeignKey('cards.id'))
    supertype_id = Column(VARCHAR(id_length), ForeignKey('supertypes.id'))

class XCardType(IdMixin, Base, DefaultMixin):

    __tablename__ = 'x_card_types'

    card_id = Column(VARCHAR(id_length), ForeignKey('cards.id'))
    type_id = Column(VARCHAR(id_length), ForeignKey('types.id'))


class XCardSubtype(IdMixin, Base, DefaultMixin):

    __tablename__ = 'x_card_subtypes'

    card_id = Column(VARCHAR(id_length), ForeignKey('cards.id'))
    subtype_id = Column(VARCHAR(id_length), ForeignKey('subtypes.id'))


class MtgCardModel(IdMixin, Base, DefaultMixin, MtgCard):
    __tablename__ = 'cards'

    __fields__ = MtgCard.__fields__ + ['raw_power', 'raw_toughness']

    multiverse_id = Column(Integer)
    name = Column(VARCHAR(200), nullable=False, index=True) # must create index for foreign keys that reference this
    set_id = Column(VARCHAR(id_length), ForeignKey('sets.id'))

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

    rulings = relationship("RulingModel", secondary="x_card_rulings")
    formats = relationship("FormatModel", secondary="x_card_formats")
    supertypes = relationship("SupertypeModel", secondary="x_card_supertypes")
    types = relationship("TypeModel", secondary=XCardType.__table__)
    subtypes = relationship("SubtypeModel", secondary=XCardSubtype.__table__)
    mana_cost = relationship("ManaCostModel", uselist=False)

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
    def friendly_mana_cost(self):
        pass

    @property
    def converted_mana_cost(self):
        cmc = 0
        if self.mana_cost:
            for mana_symbol in self.mana_cost.mana_symbols:
                cmc += mana_symbol.value
        return cmc

    @property
    def colors(self):
        colors = set()
        if self.mana_cost:
            for mana_symbol in self.mana_cost.mana_symbols:
                for mana_type in mana_symbol.mana_types:
                    if mana_type.mana_type not in ('generic', 'colorless'):
                        colors.add(mana_type.mana_type)
            return list(colors)
        else:
            return []

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
            'power': float(self.raw_power) if (self.raw_power is not None and self.raw_power.isdigit()) else self.raw_power,
            'toughness': float(self.raw_toughness) if (self.raw_toughness is not None and self.raw_toughness.isdigit()) else self.raw_toughness,
            'transformMultiverseId': self.transform_card.multiverse_id if self.transform_card else None,
            'loyalty': self.loyalty,
            'colors': self.colors,
            'types': [t.name for t in self.types],
            'subtypes': [t.name for t in self.subtypes],
            'supertypes': [t.name for t in self.supertypes],
            'cmc': self.converted_mana_cost,
            'otherArts': [{"multiverseId": c.multiverse_id} for c in self.other_arts()],
            'manaCost': self.mana_cost.get_symbol_string() if self.mana_cost else None,
            'imageUrl': self.image_url if self.multiverse_id else '',
            'allSets': [s.code for s in self.all_sets]
        }
        return {k: v for k, v in data.iteritems() if v is not None}


class MtgCardSetModel(Base, DefaultMixin, IdMixin, MtgCardSet):

    __tablename__ = 'sets'
    name = Column(VARCHAR(200))
    code = Column(VARCHAR(10))
    block = Column(VARCHAR(200))
    release_date = Column(Date)
    set_type = Column(Enum(*SET_TYPES))
    cards = relationship("MtgCardModel", backref="set")
    def __init__(self, **kwargs):
        MtgCardSet.__init__(self, **kwargs)
        IdMixin.__init__(self)

    def dictify(self):
        return {
            'name': self.name,
            'code': self.code,
            'block': self.block,
            'releaseDate': self.release_date.strftime("%m/%d/%y"),
            'setType': self.set_type
        }


class XManaTypeManaSymbol(IdMixin, Base, DefaultMixin):

    __tablename__ = "x_mana_types_mana_symbol"

    mana_symbol_id = Column(VARCHAR(id_length), ForeignKey("mana_symbols.id"))
    mana_type_id = Column(VARCHAR(id_length), ForeignKey("mana_types.id"))


class ManaSymbolModel(IdMixin, Base, DefaultMixin):

    __tablename__ = 'mana_symbols'

    value = Column(Float, default=1)
    label = Column(VARCHAR(10))
    phyrexian = Column(Boolean, default=False)
    variable = Column(Boolean, default=False)

    mana_types = relationship("ManaTypeModel", secondary=XManaTypeManaSymbol.__table__)

    @classmethod
    def get_mana_symbol(cls,
                        mana_types,
                        phyrexian=False,
                        value=1,
                        label='x',
                        variable=False):

        query = db.Session.query(ManaSymbolModel)\
                          .join(XManaTypeManaSymbol)\
                          .join(ManaTypeModel)\
                          .filter(ManaSymbolModel.phyrexian == phyrexian)\
                          .filter(ManaSymbolModel.label == label)\
                          .filter(ManaSymbolModel.variable == variable)\
                          .filter(ManaSymbolModel.value == value)

        symbols = [s for s in query.all() if set(s.mana_types) == set(mana_types)]
        if not len(symbols):
            symbol = ManaSymbolModel()
            symbol.value = value
            symbol.variable = variable
            symbol.label = label
            symbol.phyrexian = phyrexian
            for mana_type in mana_types:
                mana_type = ManaTypeModel.filter(ManaTypeModel.mana_type == mana_type).one()
                symbol.mana_types.append(mana_type)
            symbol.add()

        elif len(symbols) > 1:
            raise Warning("More than one result for this mana symbol: {}".format(locals()))
            symbol = symbols[0]

        return symbol

    def __str__(self):
        if self.variable:
            return '{{{}}}'.format(self.label)

        if [x.mana_type for x in self.mana_types] == [ManaSymbol.GENERIC]:
            return '{{{}}}'.format(int(self.value))

        symbol_str_map = {
            ManaSymbol.COLORLESS: "C",
            ManaSymbol.WHITE    : "W",
            ManaSymbol.BLUE     : "U",
            ManaSymbol.BLACK    : "B",
            ManaSymbol.RED      : "R",
            ManaSymbol.GREEN    : "G",
            ManaSymbol.VARIABLE : "X"
        }
        type_str = ""
        if self.phyrexian:
            type_str += "P/"
        type_str += '/'.join([symbol_str_map.get(mt.mana_type) for mt in self.mana_types])
        return '{{{}}}'.format(type_str)

    def __repr__(self):
        return "<{}.{} instance {} at {}>".format(self.__module__, self.__class__.__name__, [x.mana_type for x in self.mana_types], hash(self))


class ManaTypeModel(IdMixin, Base, DefaultMixin):

    __tablename__ = "mana_types"

    all_types = ["white", "blue", "black", "red", "green", "colorless", "generic", "variable"]

    mana_type = Column(Enum(*all_types))

    @classmethod
    def populate(cls):
        for mana_type in cls.all_types:
            if not cls.filter(cls.mana_type == mana_type).all():
                mt_model = cls()
                mt_model.mana_type = mana_type
                mt_model.insert()


class XManaCostManaSymbol(IdMixin, Base, DefaultMixin):

    __tablename__ = "x_mana_cost_mana_symbol"

    mana_cost_id = Column(VARCHAR(id_length), ForeignKey("mana_costs.id"))
    mana_symbol_id = Column(VARCHAR(id_length), ForeignKey("mana_symbols.id"))

class ManaCostModel(IdMixin, Base, DefaultMixin):

    __tablename__ = 'mana_costs'

    card_id = Column(VARCHAR(id_length), ForeignKey('cards.id'))

    mana_symbols = relationship("ManaSymbolModel", secondary=XManaCostManaSymbol.__table__)

    @classmethod
    def create(cls, card, mana_symbols):
        mana_cost = cls()
        mana_cost.card_id = card.id
        for s in mana_symbols:
            mana_cost.mana_symbols.append(s)
        card.mana_cost = mana_cost
        return mana_cost

    def get_symbol_string(self):
        wubrg = [ManaSymbol.VARIABLE, ManaSymbol.GENERIC, ManaSymbol.WHITE, ManaSymbol.BLUE, ManaSymbol.BLACK,
                 ManaSymbol.RED, ManaSymbol.GREEN, ManaSymbol.COLORLESS]

        sym_str = ""
        def sorting_hat(sym1, sym2):
            s1 = []
            for mt in sym1.mana_types:
                s1.append(wubrg.index(mt.mana_type))

            s2 = []
            for mt in sym2.mana_types:
                s2.append(wubrg.index(mt.mana_type))

            for i, n in enumerate(s1):
                if i >= len(s2):
                    return 1
                elif n < s2[i]:
                    return -1
                elif n > s2[i]:
                    return 1
            else:
                return 0

        sorted_cost = sorted(self.mana_symbols, cmp=sorting_hat)
        return "".join([str(x) for x in sorted_cost])
