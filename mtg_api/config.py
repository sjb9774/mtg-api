from ConfigParser import ConfigParser
import os

project_base_dir = os.path.dirname(os.path.dirname(__file__))

config = None
def init(config_type):
    global config
    if config_type.lower() == "live":
        config = Config(Config.LIVE_CONFIG_PATH, True)
    else:
        config = Config(Config.TEST_CONFIG_PATH, True)
    return config


class Config(object):

    LIVE_CONFIG_PATH = os.path.join(project_base_dir, 'conf.cfg')
    TEST_CONFIG_PATH = os.path.join(project_base_dir, 'tests/conf.cfg')

    def __init__(self, path, auto_write):
        self._parser = ConfigParser()
        self._parser.readfp(open(path))
        self._path = path
        self._auto_write = auto_write
        self.set_current_config(self)

    def __getattr__(self, attr_name):
        if hasattr(self._parser, attr_name):
            return getattr(self._parser, attr_name)
        else:
            return ConfigSection(attr_name, self._parser, self._path, self._auto_write)

    def all(self):
        d = {}
        for section in self._parser.sections():
            d[section] = {}
            for name, value in self._parser.items(section):
                d[section][name] = value

        return d

    @classmethod
    def get_current_config(cls):
        if hasattr(cls, "config"):
            return cls.config
        else:
            return None

    @classmethod
    def set_current_config(cls, config):
        cls.config = config


class ConfigSection(object):

    def __init__(self, name, parser, path, auto_write=True):
        set_attr = super(ConfigSection, self).__setattr__
        set_attr('__parser', parser)
        set_attr('__name', name)
        set_attr('__path', path)
        set_attr('__auto_write', auto_write)

    def __getattr__(self, attr_name):
        get_attr = super(ConfigSection, self).__getattribute__
        p = get_attr('__parser')
        if attr_name in ('__name', '__parser', '__path', '__auto_write'):
            return get_attr(attr_name)
        elif p.has_option(get_attr('__name'), attr_name):
            return p.get(get_attr('__name'), attr_name)
        else:
            return None

    def __setattr__(self, attr_name, value):
        if attr_name in ('_ConfigSection__name', '_ConfigSection__parser'):
            super(ConfigSection, self).__setattr__(attr_name, value)
        else:
            get_attr = super(ConfigSection, self).__getattribute__
            p = get_attr('__parser')
            if not p.has_section(get_attr('__name')):
                p.add_section(get_attr('__name'))
            p.set(get_attr('__name'), attr_name, value)
            if get_attr('__auto_write'):
                p.write(open(get_attr('__path'), 'r+'))
