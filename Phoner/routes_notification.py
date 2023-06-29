from flask import Blueprint, current_app, render_template, redirect, url_for
from bson.objectid import ObjectId

from crypt import methods
from flask import Blueprint, current_app, render_template, session, redirect, request, url_for, flash
import functools
import uuid
import datetime
from dataclasses import asdict
from Phoner.models import Notification, User,Survey, Question, Contact,ScheduledMessage, SentMessage, OpenSurvey
from Phoner.forms import ExtendedNotificationForm, NotificationForm, RegisterForm, LoginForm, SurveyForm, QuestionForm
from Phoner.model.bot import chat
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import requests
import time
import os
from dotenv import load_dotenv
from bson.objectid import ObjectId

from Phoner.routes import send_message
notification = Blueprint('notification', __name__, template_folder="templates", static_folder="static", url_prefix="/notification")

@notification.route("/test/", methods=["GET", "POST"])
#require login
def contacts_update():

    return "hi"


###Notification Center

@notification.route("/send_notification",  methods=["GET", "POST"])
def send_notification():
    age = request.form["age-group"]
    gender = request.form["gender"]
    kids = request.form["kids"]
    education = request.form["education"]
    village = request.form["village"]
   

    query = {}
    #if age:
    #    query["age"] = age
    if age:
        age_min, age_max = age.split("-")
        query["age"] = {"$gte": int(age_min), "$lte": int(age_max)}
    
    if gender:
        query["gender"] = gender

    if kids:
        query["kids"] = kids

    if education:
        query["education"] = education

    if village:
        query["village"] = village

    
    contacts = current_app.db.Contacts.find(query) 

    messageID = request.form["notification"]
    message = current_app.db.Notifications.find_one({"_id":messageID})
  

    for contact in contacts:
        print(contact["phone"],message["content"])
        result = send_message(contact["phone"],message["content"])
        
    flash("Message sent!", "success")     
    return redirect(url_for("notification.center")) 


@notification.route("/notification/send", methods=["GET", "POST"])
#require login
def notification_send():
    user_data = current_app.db.Users.find_one({"email": session["email"]}) #finds user related SMS questions
    
    user = User(**user_data)


    villages = current_app.db.Contacts.distinct("village")
    
    all_notifications = current_app.db.Notifications.find({"_id": {"$in": user.notifications }})

    
    
    return render_template("notification_send.html", notifications=all_notifications, villages=villages)

@notification.route("/notification/schedule/", methods=["GET", "POST"])
#require login
def notification_schedule():
    user_data = current_app.db.Users.find_one({"email": session["email"]}) #finds user related SMS questions
    
    user = User(**user_data)


    projects = current_app.db.Contacts.distinct("project")
    
    all_notifications = current_app.db.Notifications.find({"_id": {"$in": user.notifications }})
    return render_template("notification_schedule.html", notifications=all_notifications, projects=projects)



@notification.route("/notification", methods=["GET", "POST"])
def center():    
    user_data = current_app.db.Users.find_one({"email": session["email"]}) #finds user related SMS questions
    
    user = User(**user_data)

    all_notifications = current_app.db.Notifications.find({"_id": {"$in": user.notifications }})
    
    return render_template("notification.html", notification_data=all_notifications)

@notification.route("/add", methods=["GET", "POST"])
#@login_required
def add():
    form = NotificationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            notification = Notification(
                _id = uuid.uuid4().hex,
                title = form.title.data,
                content= form.content.data
                
            )

            current_app.db.Notifications.insert_one(asdict(notification))
            current_app.db.Users.update_one(
    {"_id": session["user_id"]}, {"$push": {"notifications": notification._id}}
)
            return redirect(url_for(".center"))
         
    return render_template("notification_new.html",
    title="Phoner - Create New Notification", form=form)

@notification.get("/notification/<string:_id>")
def notification_details(_id:str):
    
    notification_data = current_app.db.Notifications.find_one({"_id": _id})
    notification = Notification(**notification_data)
    
    #render a form and populate it with information to edit now its just view the information see udemy
    
    return render_template("notification_details.html", notification=notification)

@notification.route("/edit/<string:_id>", methods=["GET", "POST"])
def notification_edit(_id:str):
    
    notification_data = current_app.db.Notifications.find_one({"_id": _id})
    
    notification = Notification(**notification_data)
    
    form = ExtendedNotificationForm(obj=notification)

    if form.validate_on_submit():
        
        notification.title = form.title.data    
        notification.content = form.content.data
        
        notification.comment = form.comment.data
        notification.status = form.status.data
        print(asdict(notification))

        

        current_app.db.Notifications.update_one({"_id": notification._id}, {"$set": asdict(notification)})
        return redirect(url_for(".notification_details", _id=notification._id))
    return render_template("notification_form.html", notification=notification, form=form)



@notification.route("/notification/<string:_id>/delete", methods=["GET", "POST"])
#require login
def notification_delete(_id):

    current_app.db.Notifications.delete_one({"_id": _id})


    return redirect(url_for(".center"))

@notification.get("/notification/<string:_id>/rate")
def notification_rate(_id):
    rating= int(request.args.get("rating"))
    current_app.db.Notifications.update_one({"_id": _id}, {"$set":{"ratingImportance":rating}})

    return redirect(url_for(".notification_details", _id=_id))

@notification.route("/add_notificsation/", methods=["GET", "POST"])
#@login_required
def add_notificastion():
    form = NotificationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            notification = Notification(
                _id = uuid.uuid4().hex,
                title = form.title.data,
                content= form.content.data
                
            )

            current_app.db.Notifications.insert_one(asdict(notification))
            current_app.db.Users.update_one(
    {"_id": session["user_id"]}, {"$push": {"notifications": notification._id}}
)
            return redirect(url_for(".center"))
         
    return render_template("notification_new.html",
    title="Phoner - Create New Notification", form=form)
