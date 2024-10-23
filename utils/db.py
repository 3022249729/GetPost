from pymongo import MongoClient

db = None

def connect_db():
    global db
    if db is None:
        mongo_client = MongoClient("mongodb://mongo:27017/")
        db = mongo_client["cse312"]
    return db
