from flask import Flask
from config import Config
from flask_restful import Api
from flask_docs import ApiDoc

from app.resources import help
from app.resources import author


# app init
app = Flask(__name__)
app.config.from_object(Config)
api = Api(app)
# help
api.add_resource(help.Help, '/')
# author
api.add_resource(author.SearchAuthor, '/author/search')
api.add_resource(author.AuthorByID, '/author/<string:author_id>')
api.add_resource(author.AuthorByOrg,'/author/org')
api.add_resource(author.AuthorRank,'/author/rank')
#文档生成
ApiDoc(app,title='Gugoo API Doc',version='0.0.1')