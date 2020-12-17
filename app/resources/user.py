from datetime import date
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from config import Config
from app.common.util import db


def create_token(user_id):
    """
    生成token
    :param user_id: 用户id
    :return:
    """
    s = Serializer(Config.SECRET_KEY,
                   expires_in=Config.TOKEN_EXPIRATION)
    token = s.dumps({"id": user_id}).decode('ascii')
    return token


def verify_token(token):
    '''
    校验token
    :param token:
    :return: 用户信息 or None
    '''
    s = Serializer(Config.SECRET_KEY)
    try:
        data = s.loads(token)
    except Exception:
        return None
    return data["id"]


class Register(Resource):
    def post(self):
        """
        @@@
        ## 用户注册
        ### args
        参数位于body
        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    username    |    false    |    string   |    用户名，不能重复    |
        |    password    |    false    |    string   |    密码    |
        |    email    |    false    |    string   |    密码    |
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
        parser.add_argument("username", type=str, required=True)
        parser.add_argument("password", type=str, required=True)
        parser.add_argument("email", type=str, required=True)
        parser.add_argument("name", type=str, required=False)
        parser.add_argument("introduction", type=str, required=False)
        parser.add_argument("location", type=str, required=False)
        req = parser.parse_args()
        username = req.get("username")
        users = db.collection('user')
        doc = users.document(username).get()
        if doc.exists:
            return{
                'success': False,
                'message': '用户名已存在'}
        password = req.get("password")
        name = req.get("name")
        introduction = req.get("introduction")
        location = req.get("location")
        email = req.get("email")
        pwhash = generate_password_hash(
            password, method='pbkdf2:sha1', salt_length=8)
        data = {
            'username': username,
            'password': pwhash,
            'email': email,
            'name': name,
            'introduction': introduction,
            'location': location,
            'activate': False,
        }
        users.document(username).set(data)
        return{
            'success': True,
            'data': data}


class Login(Resource):
    def post(parameter_list):
        """
        @@@
        ## 用户登录
        ### args

        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    username    |    false    |    string   |    用户名   |
        |    password    |    false    |    string   |    密码    |

        ### return
        - #### data
        > | 字段 | 可能不存在 | 类型 | 备注 |
        |--------|--------|--------|--------|
        |    token    |    false    |    string   |    用于验证身份的token    |
        @@@
        """
        parser = RequestParser()
        parser.add_argument('name', type=str, required=True)
        parser.add_argument("password", type=str, required=True)
        req = parser.parse_args(strict=True)
        username = req['username']
        password = req['password']
        users = db.collection('user')
        user = users.document(username).get()
        if not user.exists:
            return{
                'success': False,
                'message': '用户名或密码错误'}, 403
        pwhash = user.to_dict()['password']
        if check_password_hash(pwhash, password):
            data = {'token': create_token(username)}
            return{
                'success': True,
                'data': data},
        else:
            return{
                'success': False,
                'message': '用户名或密码错误'}, 403
