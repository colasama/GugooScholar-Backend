from config import Config
from flask import Flask
from google.cloud import firestore


app = Flask(__name__)
app.config.from_object(Config)
db = firestore.Client()
