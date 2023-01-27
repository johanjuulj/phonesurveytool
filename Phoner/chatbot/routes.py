from flask import Blueprint, current_app, render_template, redirect, url_for
from bson.objectid import ObjectId

chatbot = Blueprint('chatbot', __name__, template_folder="templates", static_folder="static", url_prefix="/chatbot")

@chatbot.route("/welcome")
def welcome():
    return "welcome to chatbot"        
