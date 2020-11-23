from enum import auto
from flask_restful import Api
from .init import app
from . import test
from . import author

api = Api(app)
#test
api.add_resource(test.test_api, '/test')
#author
api.add_resource(author.Search,'/author/search')
api.add_resource(author.Author,'/author/<string:author_id>')