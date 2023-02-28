""" Module for setting up the app environment variables and registering the blueprints """
import os
from flask import Flask
from dotenv import load_dotenv
from pymongo import MongoClient
from Phoner.routes_survey import survey
from Phoner.routes_notification import notification
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
    app.register_blueprint(notification)
    app.register_blueprint(survey)
    return app
