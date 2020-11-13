from enum import auto
from flask_restful import Api
from .init import app
from . import test
from . import author

api = Api(app)
api.add_resource(test.test_api, '/test')
api.add_resource(author.search,'/author/search')