class Color:

    _green = ('green', 'g')
    _blue = ('blue', 'u')
    _white = ('white', 'w')
    _red = ('red', 'r')
    _black = ('black', 'b')

    # any use for this?
    _colorless = ('colorless', 'colorless')

    _all_colors = [_green, _blue, _white, _black, _red]

    def __init__(self, colors=[]):
        self.colors = []
        for color in colors:
            # split hybrid colors into their respective colors
            iterable_colors = []
            if len(color.split('/')) > 1:
                iterable_colors += color.split('/')
            else:
                iterable_colors.append(color)

            for color in iterable_colors:
                # make sure it's a real color, then append if it is real and not already in this color
                validated_color = self._get_valid_color(color)
                if validated_color and validated_color not in self.colors:
                    self.colors.append(validated_color)

    def get_colors(self):
        return tuple(self.colors)

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
        for color in self.colors:
            if color not in other.colors:
                return False
        return True

    def matches(self, other):
        return self.colors_in(other) and other.colors_in(self)

    def _get_valid_color(self, color):
        for known_color_tuple in self._all_colors:
            if color.lower() in known_color_tuple:
                return known_color_tuple[0]
        return None

    def __eq__(self, other):
        return self.matches(other)

    def __ne__(self, other):
        return not self.matches(other)

    def __str__(self):
        return ', '.join([color.capitalize() for color in self.colors])

    def __repr__(self):
        return '<Color instance ("{colors}")>'.format(colors='/'.join([color[0] for color in self.colors]))
