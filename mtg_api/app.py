from flask import Flask
from .config import Config
from .my_database import MyDatabase
from .db import setup_database
import os

TEST = "test"
LIVE = "live"

app = None
def make_app(ctx):
    global app
    app = Flask(__name__)
    app.mtg_api_ctx = ctx
    if ctx == TEST:
        config = Config(Config.TEST_CONFIG_PATH, True)
    elif ctx == LIVE:
        config = Config(Config.LIVE_CONFIG_PATH, True)
    Config.set_current_config(config)
    setup_database(MyDatabase(config))
    return app
