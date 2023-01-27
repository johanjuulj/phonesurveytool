import os
from flask import Flask
from dotenv import load_dotenv
from pymongo import MongoClient

from Phoner.chatbot.routes import chatbot
from Phoner.routes import pages

load_dotenv()


def create_app():
    app = Flask(__name__)
    
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
    
    client = MongoClient(os.environ.get("MONGO_URI"))
    app.db = client.Phoner

    app.register_blueprint(pages)
    app.register_blueprint(chatbot)
    return app


