from flask import Flask
from config import Config
from flask_restful import Api
from flask_docs import ApiDoc

from app.resources import help
from app.resources import author
from app.resources import paper


# app init
app = Flask(__name__)
app.config.from_object(Config)
api = Api(app)
# help
api.add_resource(help.Help, '/')
# author
api.add_resource(author.SearchAuthor, '/author/search')
api.add_resource(author.AuthorByID, '/author/<string:author_id>')
api.add_resource(author.AuthorDoc,'/author/<string:author_id>/paper')
api.add_resource(author.AuthorByOrg,'/author/byorg')
api.add_resource(author.AuthorRank,'/author/rank')
api.add_resource(author.AuthorRelation,'/author/<string:author_id>/relation')
# paper
api.add_resource(paper.PaperByID,'/paper/<string:paper_id>')
api.add_resource(paper.PaperRank,'/paper/rank')
api.add_resource(paper.SearchPaper,'/paper/search')
#文档生成
ApiDoc(app,title='Gugoo API Doc',version='0.0.1')