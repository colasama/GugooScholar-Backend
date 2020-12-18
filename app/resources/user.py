from app.resources import author
from app.common.util import db
from app.common.util import mail
from config import Config
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from flask_mail import Message
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import check_password_hash, generate_password_hash


def create_token(user_id):
    s = Serializer(Config.SECRET_KEY,
                   expires_in=Config.TOKEN_EXPIRATION)
    token = s.dumps({"id": user_id}).decode('ascii')
    return token


def verify_token(token):
    s = Serializer(Config.SECRET_KEY)
    try:
        data = s.loads(token)
    except Exception:
        return None
    return data["id"]


def create_authkey(email, user_id):
    s = Serializer(Config.SECRET_KEY,
                   expires_in=7200)
    token = s.dumps({"email": email, "id": user_id}).decode('ascii')
    return token


def verify_authkey(token):
    s = Serializer(Config.SECRET_KEY)
    try:
        data = s.loads(token)
    except Exception:
        return None
    return data


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
    def post(self):
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
        parser.add_argument('username', type=str, required=True)
        parser.add_argument("password", type=str, required=True)
        req = parser.parse_args()
        username = req.get('username')
        password = req.get('password')
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


class SendMail(Resource):
    def post(self):
        """
        @@@
        ## 发送验证邮件
        ### args

        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    username    |    false    |    string   |    用户名   |
        |    email    |    false    |    string   |    发送邮箱   |
        |    url    |    false    |    string   |   邮件内包含的链接    |

        示例： url为https://gugoo.fewings.xyz/#/auth
        则邮件内链接为：https://gugoo.fewings.xyz/#/auth?authkey=<authkey>

        ### return
        无data
        @@@
        """
        parser = RequestParser()
        parser.add_argument('username', type=str, required=True)
        parser.add_argument("email", type=str, required=True)
        parser.add_argument("url", type=str, required=True)
        req = parser.parse_args()
        username = req.get('username')
        users = db.collection('user')
        user = users.document(username).get()
        if not user.exists:
            return{
                'success': False,
                'message': '用户名不存在'}, 403
        email = req.get('email')
        user_email = user.to_dict()['email']
        if user_email != email:
            return{
                'success': False,
                'message': '邮箱地址不正确'}, 403
        url = req.get('url')
        msg = Message()
        msg.add_recipient(email)
        url += ('?authkey=' + create_authkey(email, username))
        msg.subject = '咕鸽学术帐号电子邮件验证'
        msg.html = f'''<p>尊敬的{username}：您好！</p>
                    <p>请点击以下链接验证您的电子邮件地址，以继续您的操作。</p>
                    <p><a href='{url}'>{url}</a></p>
                    <p>链接两小时内有效。</p>
                    <p>如果未曾要求验证该地址，您可以忽略此电子邮件。</p>
                    <p>此致</p>
                    <p>咕鸽学术团队敬上</p>'''
        msg.send(mail)
        return{
            'success': True,
            'message': '发送成功'}


class ActivateUser(Resource):
    def post(self):
        """
        @@@
        ## 通过authkey激活用户，使其activate字段为True
        ### args

        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    authkey    |    false    |    string   |    邮件链接里的authkey    |

        ### return
        无data
        @@@
        """
        parser = RequestParser()
        parser.add_argument('authkey', type=str, required=True)
        req = parser.parse_args()
        authkey = req.get('authkey')
        data = verify_authkey(authkey)
        if data == None:
            return{
                'success': False,
                'message': 'authkey无效'}, 403
        username = data['id']
        email = data['email']
        users = db.collection('user')
        user_ref = users.document(username)
        user = user_ref.get().to_dict()
        if user['email'] != email:
            return{
                'success': False,
                'message': 'authkey无效'}, 403
        user_ref.update({u'activate': True})
        return{
            'success': True,
            'message': '用户激活成功'}


class ChangeMail(Resource):
    def post(self):
        """
        @@@
        ## 更改邮箱地址，更改完成后，会变成未激活（因为只验证了老地址）
        ### args

        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    authkey    |    false    |    string   |    邮件链接里的authkey    |
        |    email    |    false    |    string   |    新的Email地址    |

        ### return
        无data
        @@@
        """
        parser = RequestParser()
        parser.add_argument('authkey', type=str, required=True)
        parser.add_argument('email', type=str, required=True)
        req = parser.parse_args()
        authkey = req.get('authkey')
        new_email = req.get('email')
        data = verify_authkey(authkey)
        if data == None:
            return{
                'success': False,
                'message': 'authkey无效'}, 403
        username = data['id']
        email = data['email']
        users = db.collection('user')
        user_ref = users.document(username)
        user = user_ref.get().to_dict()
        if user['email'] != email:
            return{
                'success': False,
                'message': 'authkey无效'}, 403
        user_ref.update({u'email': new_email, u'activate': False})
        return{
            'success': True,
            'message': '邮箱更改成功'}


class BindAuthor(Resource):
    def post(self):
        """
        @@@
        ## 认领作者

        ### header args

        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    token    |    false    |    string   |      |

        ### args

        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    author_id    |    false    |    string   |    认领的作者id   |

        ### return
        - #### data
        > | 字段 | 可能不存在 | 类型 | 备注 |
        |--------|--------|--------|--------|
        |    token    |    false    |    string   |    用于验证身份的token    |
        @@@
        """
        parser = RequestParser()
        parser.add_argument('token', type=str,
                            required=True, location='headers')
        parser.add_argument('author_id', type=str, required=True)
        req = parser.parse_args()
        token = req.get('token')
        author_id = req.get('author_id')
        username = verify_token(token)
        author_ref = db.collection('author').document(author_id)
        user_ref = db.collection('user').document(username)
        author = author_ref.get()
        if not author.exists:
            return{
                'success': False,
                'message': '作者不存在'}, 403
        if 'bind_user' in author.to_dict():
            return{
                'success': False,
                'message': '作者已被认领'}, 403
        author_ref.update({u'bind_user': username})
        user_ref.update({u'bind_author': author_id})
        return{
            'success': True,
            'message': '认领成功'}