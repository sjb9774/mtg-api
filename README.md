# mtg-api

## A simple API for gathering information about Magic cards

This repo is meant to be a simple, portable, self-contained service for retrieving information
about Magic cards. The idea is that you can clone the repo to your own server and host an instance
of the database and API yourself so you're able to keep it as private or public as your like, which
gives you control over how much of a load you want on the database. This also provides a strict decoupling
between Magic information and the application that consumes it, leading to fewer opportunities to introduce
rigidness and unnecessary dependencies in your program.

## Get started

This repo needs just a bit of setup before you can start querying. First, you'll need to make sure your system
has MySQL installed. Create a user and database for `mtg-api` then create a config file called `conf.cfg` modeled
after the `dummy-config.cfg` file included with the repo with the information filled in with your specific db setup.

You'll want to install the dependencies with `pip install -r requirements.txt`. Then run `mtg_dump.py` to populate
the database; this will probably take a little while (there are a lot of magic cards out there!). Once that's completed
you should be set to run `python runserver.py` and start querying the server and consuming that sweet, sweet JSON.

### Example
`curl -G "127.0.0.1:9000/api/card" --data-urlencode "name=Black Lotus"`
```
{
  "cards": [
    {
      "allSets": [
        "LEA",
        "LEB",
        "2ED",
        "VMA"
      ],
      "imageUrl": "http://gatherer.wizards.com/Handlers/Image.ashx?multiverseid=298&type=card",
      "manaCost": {
        "c": 0
      },
      "multiverseId": 298,
      "name": "Black Lotus",
      "rulesText": "{T}, Sacrifice Black Lotus: Add three mana of any one color to your mana pool.",
      "set": "LEB",
      "types": [
        "artifact"
      ]
    },
    {
      "allSets": [
        "LEA",
        "LEB",
        "2ED",
        "VMA"
      ],
      "imageUrl": "http://gatherer.wizards.com/Handlers/Image.ashx?multiverseid=382866&type=card",
      "manaCost": {
        "c": 0
      },
      "multiverseId": 382866,
      "name": "Black Lotus",
      "rulesText": "{T}, Sacrifice Black Lotus: Add three mana of any one color to your mana pool.",
      "set": "VMA",
      "types": [
        "artifact"
      ]
    },
    {
      "allSets": [
        "LEA",
        "LEB",
        "2ED",
        "VMA"
      ],
      "imageUrl": "http://gatherer.wizards.com/Handlers/Image.ashx?multiverseid=3&type=card",
      "manaCost": {
        "c": 0
      },
      "multiverseId": 3,
      "name": "Black Lotus",
      "rulesText": "{T}, Sacrifice Black Lotus: Add three mana of any one color to your mana pool.",
      "set": "LEA",
      "types": [
        "artifact"
      ]
    },
    {
      "allSets": [
        "LEA",
        "LEB",
        "2ED",
        "VMA"
      ],
      "manaCost": {
        "c": 0
      },
      "name": "Black Lotus",
      "rulesText": "{T}, Sacrifice Black Lotus: Add three mana of any one color to your mana pool.",
      "set": "CEI",
      "types": [
        "artifact"
      ]
    },
    {
      "allSets": [
        "LEA",
        "LEB",
        "2ED",
        "VMA"
      ],
      "manaCost": {
        "c": 0
      },
      "name": "Black Lotus",
      "rulesText": "{T}, Sacrifice Black Lotus: Add three mana of any one color to your mana pool.",
      "set": "CED",
      "types": [
        "artifact"
      ]
    },
    {
      "allSets": [
        "LEA",
        "LEB",
        "2ED",
        "VMA"
      ],
      "imageUrl": "http://gatherer.wizards.com/Handlers/Image.ashx?multiverseid=600&type=card",
      "manaCost": {
        "c": 0
      },
      "multiverseId": 600,
      "name": "Black Lotus",
      "rulesText": "{T}, Sacrifice Black Lotus: Add three mana of any one color to your mana pool.",
      "set": "2ED",
      "types": [
        "artifact"
      ]
    }
  ]
}
```
