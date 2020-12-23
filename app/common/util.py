from app.api import app
from config import Config
from flask_mail import Mail
from google.cloud import firestore
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from sonic import SearchClient


delete_field = firestore.DELETE_FIELD
db = firestore.Client()
desc = firestore.Query.DESCENDING
querycl = SearchClient("35.220.150.81", 1491, "YanG981227")
mail = Mail(app)


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
