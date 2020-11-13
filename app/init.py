from config import Config
from flask import Flask
from google.cloud import firestore
from sonic import SearchClient


app = Flask(__name__)
app.config.from_object(Config)
db = firestore.Client()
querycl = SearchClient("35.220.150.81", 1491, "YanG981227")