from flask_restful import Api
from .init import app
from . import test


api = Api(app)
api.add_resource(test.test_api, '/test')
