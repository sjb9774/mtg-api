from mtg_api.db import setup_database
from mtg_api.my_database import MyDatabase
from mtg_api.config import Config
my_database = MyDatabase(Config(Config.LIVE_CONFIG_PATH, True))
setup_database(my_database)
from mtg_api.models.magic import *
from mtg_api.models.users import *
from mtg_api.models.sessions import *
my_database.drop_tables()
my_database.drop_database()
my_database.make_database()
my_database.make_tables()
