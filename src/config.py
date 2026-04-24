import os

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID","")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY","")
DATA_FOLDER = os.getenv("DATA_FOLDER", "data")
DATA_LAKE_SAS = os.getenv("DATA_LAKE_SAS","")
HOST = os.getenv("HOST","127.0.0.1")
PORT = int(os.getenv("PORT",8000))
TOKEN = os.getenv("TOKEN")