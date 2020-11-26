from google.cloud import firestore
from sonic import SearchClient


db = firestore.Client()
desc = firestore.Query.DESCENDING
querycl = SearchClient("35.220.150.81", 1491, "YanG981227")