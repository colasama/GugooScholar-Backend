from flask_restful import Resource, reqparse
from google.cloud import firestore
from .init import db


class test_api(Resource):
    def get(self):
        users_ref = db.collection(u'users')
        docs = users_ref.stream()
        ans = []
        for doc in docs:
            ans.append(doc.to_dict())
        return {'result': ans}
