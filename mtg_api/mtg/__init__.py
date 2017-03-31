from itertools import combinations
COLORS = ['b', 'g', 'r', 'u', 'w', 'c']
ALL_COLOR_COMBINATIONS = []
for i in xrange(1, len(COLORS) + 1):
    combinations_of_size_i = combinations(COLORS, i)
    for combination in combinations_of_size_i:
        ALL_COLOR_COMBINATIONS.append(combination)

TYPES = [
    'artifact',
    'enchantment',
    'land',
    'summon',
    'instant',
    'sorcery',
    'planeswalker',
    'creature'
]

SET_TYPES = [
    "promo",
    "expansion",
    "core",
    "vanguard",
    "reprint",
    "starter",
    "box",
    "duel deck",
    "un",
    "planechase",
    "commander",
    "masters",
    "premium deck",
    "from the vault",
    "conspiracy",
    "archenemy",
    "masterpiece"
]
