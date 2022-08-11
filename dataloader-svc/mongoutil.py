
from pymongo import MongoClient
import os


class MongoConnector:
	conn = None
	srv = "mongodb+srv://{username}:{password}@cluster0.sjuby.mongodb.net/?retryWrites=true&w=majority"

	@classmethod
	def connect(cls):
		if cls.conn is None:
			db_srv = cls.srv.format(
				username=os.getenv("MONGO_USER", "<appuser>"), 
				password=os.getenv("MONGO_PASSWORD", "<password>")
				)
			cls.conn = MongoClient(db_srv)
		return cls.conn

	@classmethod
	def disconnect(cls):
		cls.conn.close()
		cls.conn = None