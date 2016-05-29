# this class is meant to simply ensure that derived classes will always have attributes
# some attributes defined, those attributes being enumerated in __fields__. Just avoids
# having to write self.var = None for classes that have a lot of attributes that may needs
# to be defined but not necessarily initialized
class SmartObject(object):

    __fields__ = []

    def __init__(self, **kwargs):
        for field in self.__fields__:
            try:
                setattr(self, field, kwargs.get(field, None))
            except:
                pass

    def __iter__(self):
        for field in self.__fields__:
            yield field, getattr(self, field)


class MtgCardSet(SmartObject):

    __fields__ = ['name', 'code', 'block', 'release_date', 'set_type']

    def __init__(self, **kwargs):
        super(MtgCardSet, self).__init__(**kwargs)


class MtgCard(SmartObject):

    __fields__ = ['name', 'colors', 'legendary', 'artist', 'set_id',
                  'promo', 'foil', 'power', 'toughness', 'mana_cost', 'loyalty',
                  'transform', 'half', 'rarity', 'multiverse_id', 'text', 'flavor']

    def __init__(self, **kwargs):
        super(MtgCard, self).__init__(**kwargs)

    def __iter__(self):
        for field in self.__fields__:
            if hasattr(self, field) and getattr(self, field):
                yield field, getattr(self, field)

from mtg_api.mtg.colors import Color

class ManaSymbol:

    def __init__(self, colors=None, x=False, phyrexian=False, value=None, label=None):
        # label is a special parameter that only matters for X-cost symbols, it can be
        # 'x', 'y', or 'z' (see Ultimate Nightmare of Wizards Of The Coast Customer Service)
        #import pudb; pudb.set_trace()
        self.colors = []
        self._color_abbrs = []
        self.label = label
        if colors:
            for color in colors:
                c = Color(color)
                if c.abbreviation not in self._color_abbrs:
                    self.colors.append(c)
                    self._color_abbrs.append(c.abbreviation)

        if not colors or ('c' in colors and len(colors) == 1):
            self.c = True
            self._color_abbrs = ['N']
        else:
            self.c = False

        if colors and x:
            raise ValueError('X-cost mana-symbols aren\'t colored.')

        if value is not None:
            self.value = value
        elif x:
            self.value = 0
        else:
            self.value = 1
        self.x = x
        self.phyrexian = phyrexian

    def symbol(self):

        if self.x:
            return '{' + self.label + '}'
        color_array = '/'.join(sorted([color.abbreviation for color in self.colors]) + (['p'] if self.phyrexian else []))
        #import pudb; pudb.set_trace()
        if self.c:
            if color_array:
                slash = '/'
            else:
                slash = ''
            return '{'+ str(self.value) + slash + color_array + '}'
        return '{' + color_array + '}'

    def converted_mana_cost(self):
        if self.x:
            return 0
        else:
            return self.value

    def get_colors(self):
        return sorted(self.colors)

    def is_hybrid(self):
        return len(self.get_colors()) > 1

    def __hash__(self):
        return hash(self())

    def __call__(self):
        return self.symbol()

    def __repr__(self):
        return '<ManaSymbol instance "{symbol}" at {address}>'.format(symbol=self(),
                                                                      address=hex(id(self)))

class Type:

    def __init__(self, name=None):
        self.name = name

class Subtype:

    def __init__(self, name=None):
        self.name = name
