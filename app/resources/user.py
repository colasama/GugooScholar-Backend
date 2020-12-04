from flask_restful import Resource
from flask_restful.reqparse import RequestParser

from app.common.util import db

from firebase_admin import auth


class Register(Resource):
    def post(self):
        """
        @@@
        ## 新用户首次登录添加个人信息

        ### header args
        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    token    |    false    |    string   |    identity platform登录获取的token    |
        ### args

        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    username    |    false    |    string   |    用户名，可以重复，不用于登录    |
        |    name    |    true    |    string   |   真实姓名   |
        |    introduction    |    true    |    string   |   自我介绍   |
        |    location    |    true    |    string   |   用户位置   |

        ### return
        - #### data
        > | 字段 | 可能不存在 | 类型 | 备注 |
        |--------|--------|--------|--------|
        |    id    |    false    |    string   |    用户id    |
        @@@
        """
        parser = RequestParser()
        parser.add_argument('token', type=str,
                            location='headers', required=True)
        parser.add_argument("username", type=str, required=True)
        parser.add_argument("name", type=str, required=False)
        parser.add_argument("introduction", type=str, required=False)
        parser.add_argument("location", type=str, required=False)
        req = parser.parse_args()
        id_token = req.get("token")
        username = req.get("username")
        name = req.get("name")
        introduction = req.get("introduction")
        location = req.get("location")
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        data = {
            'username': username,
            'name': name,
            'introduction': introduction,
            'location': location,
        }
        user = db.collection(u'users').document(uid).get()
        if user.exists:
            return{
                'success': False,
                'message': '用户已存在'}, 400
        else:
            db.collection(u'users').document(uid).set(data)
            return{
                'success': True,
                'data': {'id': uid}}
