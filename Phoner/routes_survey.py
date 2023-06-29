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
from Phoner.routes import send_message
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import requests
import time
import os
from dotenv import load_dotenv
from bson.objectid import ObjectId


survey = Blueprint('survey', __name__, template_folder="templates", static_folder="static", url_prefix="/survey")


###SURVEY

@survey.route("/survey", methods=["GET", "POST"])
def center():

    user_data = current_app.db.Users.find_one({"email": session["email"]}) #finds user related SMS questions
   
    user = User(**user_data)
    
    question_data = current_app.db.Questions.find({"_id": {"$in": user.questions}})
    survey_data = current_app.db.Surveys.find({"_id": {"$in": user.surveys}})
    
    return render_template(
        "survey.html", survey_data=survey_data, question_data=question_data
    )

@survey.route("/send", methods=["GET", "POST"])
def send():
    age = request.form["age-group"]
    gender = request.form["gender"]
    kids = request.form["kids"]
    education = request.form["education"]
    village = request.form["village"]
   

    query = {}
 
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
    survey_id = request.form["survey"]
    
    
    survey = current_app.db.Surveys.find_one({"_id":survey_id})
    
    questions = current_app.db.Questions.find({"_id": {"$in": survey["questions"]}})
    questionlist = []   
    for question in questions:

        questionlist.append(question["content"])

   
    

    for contact in contacts:
        
           
        opensurvey = OpenSurvey(
            contact=contact["phone"],
            questions=questionlist) 
        print(contact["phone"],questionlist[0])  
        send_message(contact["phone"],questionlist[0])
        current_app.db.OpenSurvey.insert_one(asdict(opensurvey))
 
    flash("Message sent!", "success")     
    return redirect(url_for(".center"))#render survey + buzz message sent

@survey.route("/add", methods=["GET", "POST"])
def add():
    form = SurveyForm()

    if form.validate_on_submit():
        survey = Survey(
            _id=uuid.uuid4().hex,
            title=form.title.data,
            content=form.content.data
        )
        current_app.db.Surveys.insert_one(asdict(survey))
        current_app.db.Users.update_one(
    {"_id": session["user_id"]}, {"$push": {"surveys": survey._id}}
)  
        

        flash("Survey registered successfully", "success")

        return redirect(url_for(".center"))

    return render_template(
        "survey_add.html", title="Add new survey", form=form
    )

@survey.route("/edit/<string:_id>", methods=["GET", "POST"])
def edit(_id:str):
    
    survey_data = current_app.db.Surveys.find_one({"_id": _id})
    
    survey = Survey(**survey_data)
    
    form = SurveyForm(obj=survey)

    if form.validate_on_submit():
        
        survey.title = form.title.data    
        survey.content = form.content.data
        

        

        current_app.db.Surveys.update_one({"_id": survey._id}, {"$set": asdict(survey)})
        return redirect(url_for(".survey_details", _id=survey._id))
    return render_template("survey_form.html", survey=survey, form=form)

@survey.route("/delete/<string:_id>", methods=["GET", "POST"])
def delete(_id:str):
    current_app.db.Surveys.delete_one({"_id": _id})


    return redirect(url_for(".center"))



@survey.get("/survey/<string:_id>")
def survey_details(_id:str):
    
    survey_data = current_app.db.Surveys.find_one({"_id": _id})
    survey = Survey(**survey_data)

    survey_questions = current_app.db.Questions.find({"_id": {"$in": survey.questions}})
    
    return render_template("survey_details.html", survey=survey, survey_questions=survey_questions)






########## FIX ABOVE / stream line the add survey question routing

@survey.route("/survey_question/<string:_id>/<string:q_id>/remove", methods=["GET", "POST"])
#require login
def survey_question_remove(_id, q_id):

    
    current_app.db.Surveys.update_one({'_id': _id, },
                            { '$pull': { "questions": q_id }})

    return redirect(url_for(".survey_details", _id=_id))


@survey.route("/survey/send", methods=["GET", "POST"])
#require login
def survey_send():
    user_data = current_app.db.Users.find_one({"email": session["email"]}) #finds user related SMS questions
    
    user = User(**user_data)


    projects = current_app.db.Contacts.distinct("project")
    
    all_surveys = current_app.db.Surveys.find({"_id": {"$in": user.surveys }})


    
    return render_template("survey_send.html", surveys=all_surveys, projects=projects)

@survey.route("/schedule", methods=["GET", "POST"])
#require login
def schedule():
    user_data = current_app.db.Users.find_one({"email": session["email"]}) #finds user related SMS questions
    
    user = User(**user_data)


    projects = current_app.db.Contacts.distinct("project")
    
    all_surveys = current_app.db.Surveys.find({"_id": {"$in": user.surveys }})
    return render_template("survey_schedule.html", surveys=all_surveys, projects=projects)



## creates a new question
@survey.route("/question_create", methods=["GET", "POST"])
def question_create():
    form = QuestionForm()

    if form.validate_on_submit():
        question = Question(
            _id=uuid.uuid4().hex,
            title=form.title.data,
            content=form.content.data
        )

        
        current_app.db.Questions.insert_one(asdict(question))
        current_app.db.Users.update_one(
    {"_id": session["user_id"]}, {"$push": {"questions": question._id}}
)  

        flash("Question registered successfully", "success")

        return redirect(url_for(".center"))

    return render_template(
        "question_create.html", title="Add new question", form=form
    )

### List all possible questions to add
@survey.route("/question_add/<string:_id>/", methods=["GET", "POST"])
#require login
def question_add_to_survey(_id:str):


    
  #  if request.method == 'POST':
   #     #find survey form
    #    print("I posted")
     #   pass
   
    user_data = current_app.db.Users.find_one({"email": session["email"]}) 
   
    user = User(**user_data)
    
    question_data = current_app.db.Questions.find({"_id": {"$in": user.questions}})


    survey_data = current_app.db.Surveys.find_one({"_id": _id})
    survey = Survey(**survey_data)


    return render_template("survey_question_add.html", survey=survey, question_data=question_data)

##adds question to survey
@survey.route("/question_add/<string:_id>/<string:q_id>/", methods=["GET", "POST"])
#require login
def question_addq(_id:str, q_id:str):
    

    current_app.db.Surveys.update_one(    {"_id": _id}, {"$push": {"questions": q_id}})
    

    user_data = current_app.db.Users.find_one({"email": session["email"]}) 
   
    user = User(**user_data)
    
    question_data = current_app.db.Questions.find({"_id": {"$in": user.questions}})


    survey_data = current_app.db.Surveys.find_one({"_id": _id})
    survey = Survey(**survey_data)


    return redirect(url_for(".survey_details", _id=_id))

    

#question details
@survey.get("/question/<string:_id>")
def question_details(_id:str):
    
    question_data = current_app.db.Questions.find_one({"_id": _id})
    question = Question(**question_data)
    
    #render a form and populate it with information to edit now its just view the information see udemy
    
    return render_template("question_details.html", question=question)

@survey.route("/question_edit/<string:_id>", methods=["GET", "POST"])
def question_edit(_id:str):
    
    question_data = current_app.db.Questions.find_one({"_id": _id})
    
    question = Question(**question_data)
    
    form = QuestionForm(obj=question)

    if form.validate_on_submit():
        
        question.title = form.title.data    
        question.content = form.content.data
        
        #notification.comment = form.comment.data
        #notification.status = form.status.data
        

        

        current_app.db.Questions.update_one({"_id": question._id}, {"$set": asdict(question)})
        return redirect(url_for(".question_details", _id=question._id))
    return render_template("question_form.html", question=question, form=form)



@survey.route("/question/<string:_id>/delete", methods=["GET", "POST"])
def question_delete(_id):

    current_app.db.Questions.delete_one({"_id": _id})


    return redirect(url_for(".center"))
