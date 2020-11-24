from flask_restful import Resource
from flask_restful.reqparse import RequestParser

from app.common.util import db
from app.common.util import querycl


class Search(Resource):
    def get(self):
        parser = RequestParser()
        parser.add_argument("words", type=str,
                            location="args", required=True)
        parser.add_argument("start_at", type=int,
                            location="args", required=False)
        req = parser.parse_args()
        words = req.get("words")
        offset = req.get("start_at")
        print(offset)
        author_ids = querycl.query(
            "author", "name", terms=words, offset=offset, limit=10)
        authors = []
        for id in author_ids:
            authors.append(db.collection(
                'author').document(id).get().to_dict())
        return{'data': authors}


class Author(Resource):
    def get(self, author_id):
        auhtor = db.collection('author').document(author_id).get()
        if auhtor.exists:
            return{
                'success': True,
                'data': auhtor.to_dict()}
        else:
            return{
                'success': False,
                'message': '作者不存在'}, 404
