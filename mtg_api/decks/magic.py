class SmartObject:

    def __init__(self, **kwargs):
        for field in self.__fields__:
            setattr(self, field, kwargs.get(field, None))

class MtgCardSet(SmartObject):

    __fields__ = ['name', 'code', 'release_date']

    def __init__(self, **kwargs):
        super(self, MtgCardSet).__init__(**kwargs)

class MtgCard(SmartObject):

    __fields__ = ['name', 'color', 'type', 'subtype', 'legendary', 'artist', 'set',
                  'promo', 'foil', 'power', 'toughness', 'mana_cost', 'loyalty',
                  'transform', 'half']

    def __init__(self, **kwargs):
        super(self, MtgCard).__init__(self, **kwargs)
