from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()


class MongoConnector:
    conn = None
    srv = "mongodb+srv://{username}:{password}@{db_host}/?retryWrites=true&w=majority"

    @classmethod
    def connect(cls):
        if cls.conn is None:
            db_srv = cls.srv.format(
                username=os.getenv("MONGO_USER", "<appuser>"),
                password=os.getenv("MONGO_PASSWORD", "<password>"),
                db_host=os.getenv("MONGO_DB_HOST", "<db_host>")
            )
            cls.conn = MongoClient(db_srv)
        return cls.conn

    @classmethod
    def disconnect(cls):
        cls.conn.close()
        cls.conn = None
