if __name__ == "__main__":
    from mtg_api.app import make_app
    app = make_app("live")
    from mtg_api.endpoints import *
    app.run(debug=True, host='127.0.0.1', port=9000)
