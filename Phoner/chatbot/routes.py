from flask import Blueprint, current_app, render_template, redirect, url_for
from bson.objectid import ObjectId

chatbot = Blueprint('chatbot', __name__, template_folder="/chatbot/templates", static_folder="static", url_prefix="/chatbot")

@chatbot.route("/welcome")
def welcome():
    return "welcome to chatbot"        


@chatbot.route("/chatbot", methods=["GET", "POST"])
def foo():
    all_unsorted = current_app.db.BotResponseUnSorted.find()

    return render_template(
        "chatbot.html", all_unsorted=all_unsorted
    )