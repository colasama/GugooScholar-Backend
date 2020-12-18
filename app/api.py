from flask import Flask
from config import Config
from flask_restful import Api
from flask_docs import ApiDoc
from flask_compress import Compress
from flask_cors import CORS


# app init
app = Flask(__name__)
app.config.from_object(Config)
from app.resources import help, user, author, paper

#add api
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
api.add_resource(paper.PaperDoi,'/paper/doi')
api.add_resource(paper.PaperVenue,'/paper/venue')
api.add_resource(paper.GetField,'/paper/field')
#user
api.add_resource(user.Register,'/user/register')
api.add_resource(user.Login,'/user/login')
api.add_resource(user.SendMail,'/user/sendmail')
api.add_resource(user.ActivateUser,'/user/activate')
api.add_resource(user.ChangeMail,'/user/changemail')
#文档生成
ApiDoc(app,title='Gugoo API Doc',version='0.1.1')
#压缩
Compress(app)
#跨域
CORS(app, supports_credentials=True)