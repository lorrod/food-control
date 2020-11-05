from config import Config



import os
import base64
from flask import Flask
from config import Config 				# Project configuration import
from flask_pymongo import PyMongo



# Create Flask app, load app.config
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = b'eHk\x8d\xd9\x18\xf1\xd9)#\xaaf\x8aK=<'#os.environ.get("SECRET_KEY")

# PyMongo DB initialization
mongo = PyMongo(app)


WEBHOOK_HOST = app.config["WEBHOOK_HOST"]
WEBHOOK_PORT = app.config["WEBHOOK_PORT"]




#logger = telebot.logger
#telebot.logger.setLevel(logging.INFO)



import views
