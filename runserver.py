if __name__ == "__main__":
    from mtg_api import app
    from mtg_api.endpoints import *
    app.run(debug=True, host='127.0.0.1', port=9000)
