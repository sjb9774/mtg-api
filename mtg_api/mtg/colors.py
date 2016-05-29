class Color:

    def __init__(self, color):
        if color.lower() in ColorIdentity._colors_abbr_to_full:
            self.color = ColorIdentity._colors_abbr_to_full[color.lower()]
            self.abbreviation = color.lower()
        elif color.lower() in ColorIdentity._colors_full_to_abbr:
            self.color = color.lower()
            self.abbreviation = ColorIdentity._colors_full_to_abbr[self.color]
        else:
            raise ValueError('"{color}" is not a valid color.'.format(**locals()))

    def __eq__(self, other):
        return self.color == other.color

    def __ne__(self, other):
        return self.color != other.color

    def __gt__(self, other):
        return self.abbreviation > other.abbreviation

    def __lt__(self, other):
        return self.abbreviation < other.abbreviation

    def __ge__(self, other):
        return self > other or self == other

    def __le__(self, other):
        return self < other or self == other

    def __hash__(self):
        return hash(self.color)

    def __repr__(self):
        return "<{color_name} Color instance at {address}>".format(color_name=self.color.capitalize(),
                                                                   address=hex(id(self)))


class ColorIdentity:

    _green = ('green', 'g')
    _blue = ('blue', 'u')
    _white = ('white', 'w')
    _red = ('red', 'r')
    _black = ('black', 'b')

    _colors_abbr_to_full = {
        'u': 'blue',
        'b': 'black',
        'r': 'red',
        'g': 'green',
        'w': 'white',
        'c': 'colorless'
    }

    _colors_full_to_abbr = {
        'blue': 'u',
        'black': 'b',
        'red': 'r',
        'green': 'g',
        'white': 'w',
        'colorless': 'c'
    }

    # any use for this?
    _colorless = ('cs', 'colorless')

    _all_colors = [_green, _blue, _white, _black, _red]

    def __init__(self, *colors):
        self.colors = set()
        for color in colors:
            # split hybrid colors into their respective colors
            iterable_colors = set()
            if len(color.split('/')) > 1:
                iterable_colors.union(set(color.split('/')))
            else:
                iterable_colors.add(color)

            for color in iterable_colors:
                # make sure it's a real color, then append if it is real
                validated_color = self._get_valid_color(color)
                if validated_color:
                    self.colors.add(validated_color)

    def add_color(self, color):
        validated_color = self._get_valid_color(color)
        if validated_color:
            self.colors.add(validated_color)

    def get_colors(self):
        return sorted(self.colors)

    def is_(self, color):
        return self._get_valid_color(color) in self.colors

    def is_colorless(self):
        return len(self.colors) == 0

    def is_multicolored(self):
        return len(self.colors) > 1

    def is_blue(self):
        return 'blue' in self.colors

    def is_green(self):
        return 'green' in self.colors

    def is_black(self):
        return 'black' in self.colors

    def is_red(self):
        return 'red' in self.colors

    def is_white(self):
        return 'white' in self.colors

    def is_gold(self):
        return self.is_multicolored()

    def colors_in(self, other):
        self.colors.issubset(other.colors)

    def matches(self, other):
        return self.colors == other.colors

    def _get_valid_color(self, color):
        return Color(color)

    def __eq__(self, other):
        return self.matches(other)

    def __ne__(self, other):
        return not self.matches(other)

    def __str__(self):
        return ', '.join([color.capitalize() for color in self.colors])

    def __repr__(self):
        return '<Color instance ("{colors}") at {address}>'.format(colors='/'.join([color.abbreviation for color in self.colors]),
                                                                   address=hex(id(self)))
