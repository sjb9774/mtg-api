from flask import render_template, request
from mtg_api.app import app
import functools
from mtg_api.utils.users import get_active_user
from mtg_api.db import db_instance as db


def custom_route(rule, **options):
    def decorator(f):
        endpoint = options.pop('endpoint', None)
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            get_args = {}
            if request.args:
                get_args = request.args.to_dict()
            post_args = {}
            if request.form:
                post_args = request.form.to_dict()
            if options.get('methods'):
                methods = options.get('methods')
                if 'GET' in methods and 'POST' in methods:
                    results = f(*args, get_args=get_args, post_args=post_args, **kwargs)
                elif 'GET' in methods:
                    results = f(*args, get_args=get_args, **kwargs)
                elif 'POST' in methods:
                    results = f(*args, post_args=post_args, **kwargs)
                else:
                    results = f(*args, **kwargs)
                db.Session.close()
                return results

        app.add_url_rule(rule, endpoint, wrapper, **options)
        return wrapper
    return decorator

def custom_render(template_path, **kwargs):
    return render_template(template_path, active_user=get_active_user(), **kwargs)
