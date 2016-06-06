from flask import render_template, request
from mtg_api.app import app
import functools
from mtg_api.utils.users import get_active_user
from mtg_api.db import db_instance as db
import urllib
import types

class ApiMapper(object):

    def __init__(self):
        pass

    @classmethod
    def register(cls, function, endpoint):
        ''' Takes an exposed api function (defined as a function that has been decorated with custom_route)
        and its assigned endpoint and creates a new method on the ApiMapper class named after that function.
        This new method takes an SqlAlchemy model instance and a list of attribute-names and constructs the
        url one would need to request in order to get information about the model passed.

        example
        >> ApiMapper.api_get_card(cardModel, ["multiverse_id"])
        '/api/card?multiverseId=256655'
        '''
        def fn(cls, model, kwargs_to_pass):
            query_dict = {}
            for kwarg in kwargs_to_pass:
                if hasattr(model, kwarg):
                    query_dict[kwarg] = getattr(model, kwarg)
            query_str = urllib.urlencode(query_dict)
            return '{endpoint}?{qstr}'.format(endpoint=endpoint, qstr=query_str)
        # a little nonsense because Python 2.x likes to make dynamically adding methods complicated
        bound_method = types.MethodType(fn, ApiMapper, ApiMapper)
        setattr(cls, function.func_name, bound_method)





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
        ApiMapper.register(f, rule)
        app.add_url_rule(rule, endpoint, wrapper, **options)
        return wrapper
    return decorator

def custom_render(template_path, **kwargs):
    return render_template(template_path, active_user=get_active_user(), **kwargs)
