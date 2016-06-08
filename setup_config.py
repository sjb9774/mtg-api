import os
from argparse import ArgumentParser
from mtg_api.config import project_base_dir
import sys

config_structure = [
    {"section": "database",
    "options": [
            {"key": "username", "help": "The username of the database-user you wish to be associated with mtg-api."},
            {"key": "password", "help": "The password of the database-user."},
            {"key": "host", "help": "The database address.", "default": "localhost"},
            {"key": "dbserver", "help": "The database server-type.", "default": "mysql"},
            {"key": "dbname", "help": "The name of the database mtg-api should use.", "default": "mtg_api"},
            {"key": "dbapi", "help": "The api type of the server.", "default": "mysqldb"},
            {"key": "uri", "default": r"%(dbserver)s+%(dbapi)s://%(username)s:%(password)s@%(host)s/%(dbname)s?charset=utf8"}
        ]
    },
    {"section": "sqlalchemy",
    "options": [
            {"key": "pool_size", "default": 100},
            {"key": "pool_recycle", "default": 280}
        ]
    },
    {"section": "mtg",
    "options": [
            {"key": "mtgjson_path", "help": "Path to your mtgjson .json file.", "default": os.path.join(project_base_dir, "mtg_api", "DATA", "sets.json")}
        ]
    }
]

if __name__ == "__main__":
    if os.path.exists(os.path.join(project_base_dir, "conf.cfg")):
        print "conf.cfg already exists! Delete the file first if you wish to run this setup tool."
        sys.exit()
    parser = ArgumentParser()
    config_text = ""

    for section in config_structure:
        config_text += "[{}]\n".format(section.get("section"))
        for option in section.get("options"):
            # assume if there's no "help" key that we just want to save the default
            value = None
            while value == None:
                if option.get("help"):
                    prompt = option.get("help")
                    prompt += " (default: {})\n".format(option.get("default")) if option.get("default") else "\n"
                    value = raw_input(prompt) or option.get("default")
                elif option.get("default"):
                    value = option.get("default")
                else:
                    raise StandardError("Dict has no 'help' or 'key' entries.")
            config_text += "{key} = {value}\n".format(key=option.get('key'), value=value)
        config_text += "\n"

    with open("conf.cfg", 'w') as f:
        f.write(config_text)
    print "Config file written to ./conf.cfg"
