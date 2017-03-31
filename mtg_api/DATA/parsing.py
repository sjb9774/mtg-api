import re
from mtg_api.models.magic import MtgCardModel, MtgCardSetModel, ManaSymbolModel
from mtg_api.models.magic import ManaCostModel, TypeModel, RulingModel, XCardRuling
from mtg_api.models.magic import SubtypeModel, FormatModel, ManaTypeModel
from mtg_api.models.magic import XManaTypeManaSymbol
from mtg_api.mtg.magic import ManaSymbol

def parse_mana_symbol(txt):
    mana_symbol = ManaSymbolModel()
    mana_symbol.value = 1
    mana_types = []

    costs = {
        "w": ManaSymbol.WHITE,
        "u": ManaSymbol.BLUE,
        "b": ManaSymbol.BLACK,
        "r": ManaSymbol.RED,
        "g": ManaSymbol.GREEN,
        "c": ManaSymbol.COLORLESS
    }
    symbol_regx_str = r'\s*\{([\w\d/]+)\}\s*'
    symbol_regx = re.compile(symbol_regx_str)
    value = symbol_regx.findall(txt)[0]
    if value.isdigit():
        mana_types.append(ManaSymbol.GENERIC)
        mana_symbol.value = int(value)
    else:
        if value.lower() in costs:
            mana_types.append(costs[value.lower()])
        elif value.lower() in ("x", "y", "z"):
            mana_types.append(ManaSymbol.VARIABLE)
            mana_symbol.value = 0
        elif "/" in value:
            pieces = value.lower().split("/")
            if "h" in pieces:
                mana_symbol.value = .5
            if "p" in pieces:
                mana_symbol.phyrexian = True

            for piece in pieces:
                if piece.isdigit():
                    mana_symbol.value = int(piece)
                elif piece.lower() in costs:
                    mana_types.append(costs[piece])

    for mt in mana_types:
        mtm = ManaTypeModel.filter_by(mana_type=mt).one()
        mana_symbol.mana_types.append(mtm)

    return mana_symbol

def parse_mana_cost(txt):
    mana_cost_regx_str = r'\s*(\{[\w\d/]+\})\s*'
    mana_cost_regx = re.compile(mana_cost_regx_str)
    symbols = []

    for token in mana_cost_regx.findall(txt):
        symbols.append(parse_mana_symbol(token))

    return ManaCostModel(symbols)

def parse_format(txt):
    pass

def parse_power_toughness(txt):
    power = None
    if txt == "*":
        return 0
    elif not txt:
        return None
    else:
        try:
            power = float(txt)
        except ValueError:
            power = 0
        except KeyError:
            power = None
        except StandardError:
            import pudb; pudb.set_trace()
        return power

def parse_card(txt):
    pass

def parse_types(txt):
    pass

def parse_subtypes(txt):
    pass

def parse_ruling(ruling_dict):
    r = RulingModel()
    r.date = ruling_dict['date']
    r.ruling = ruling_dict['text']
    return r
