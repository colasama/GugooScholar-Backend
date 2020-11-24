from flask import Flask
from config import Config
from flask_restful import Api

from app.resources import help
from app.resources import author


# app init
app = Flask(__name__)
app.config.from_object(Config)
api = Api(app)
# test
api.add_resource(help.Hello, '/')
# author
api.add_resource(author.Search, '/author/search')
api.add_resource(author.Author, '/author/<string:author_id>')
