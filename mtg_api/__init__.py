from flask import Flask
from mtg_api.config import Config, TEST_CONFIG_PATH, CONFIG_PATH
import os

TEST = "test"
LIVE = "live"

app = None
def make_app(ctx):
    global app
    app = Flask(__name__)
    if ctx == TEST:
        app.custom_config = Config(TEST_CONFIG_PATH, True)
    elif ctx == LIVE:
        app.custom_config = Config(CONFIG_PATH, True)
    return app
