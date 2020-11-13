from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from google.cloud import firestore

from .init import db
from .init import querycl

class search(Resource):
    def get(self):
        parser = RequestParser()
        parser.add_argument("words", type=str,
                            location="args", required=True)
        req = parser.parse_args()
        words = req.get("words")
        print(words)
        res = querycl.query("author", "name", words, limit=10)
        return{'data': res}
