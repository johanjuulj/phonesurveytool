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

load_dotenv()

from passlib.hash import pbkdf2_sha256
pages = Blueprint(
    "pages", __name__, template_folder="templates", static_folder="static"
)


###Utilities

@pages.cli.command()
def scheduled():
    
    scheduledMessages = current_app.db.ScheduledMessage.find()
    
    for message in scheduledMessages:
        if message["date"] == message["date"]:
            listofnumbers = current_app.db.Contacts.find({}) #phone numbers
            messageContent = current_app.db.Notifications.find_one({"title": message["messageTitle"]})
            for number in listofnumbers:
                results = send_message(number, messageContent["content"] )
                sentmessage = SentMessage(
            _id=uuid.uuid4().hex,
            project=message["project"],
            nors="Notification",
            date=datetime.datetime.now(),
            response=results
        )
                current_app.db.SentMessages.insert_one(asdict(sentmessage)) 
                current_app.db.ScheduledMessage.delete_one({"_id": message._id})
            

                  




def send_message(number, _message):
    account_sid = os.environ.get("TWILIO_SID")
    auth_token = os.environ.get("AUTH_TOKEN") 
    client = Client(account_sid, auth_token) 
   
    message = client.messages.create( 
                              from_='whatsapp:+14155238886',  
                              body=f'{_message}',      
                              to=f'whatsapp:{number}' 
                          ) 
    
    return message.sid


def login_required(route):  
    @functools.wraps(route)  #function that replaces any end-point and runs a login check
    def route_wrapper(*args, **kwargs):
        if session.get("email") is None:
            return redirect(url_for(".login"))

        return route(*args, **kwargs)

    return route_wrapper


##SEND AND RECIEVE ENDPOINTS
@pages.route("/send_notification",  methods=["GET", "POST"])
def send_notification():
    project = request.form["project"]
    messageID = request.form["notification"]
    message = current_app.db.Notifications.find_one({"_id":messageID})
  

    contacts = current_app.db.Contacts.find() #update queru to only take project specifc to minimise load
    results = []
    for contact in contacts:
        if contact["project"] == project:
            result = send_message(contact["phone"],message["content"])
          
            results.append(result) 
           
    sentmessage = SentMessage(
            _id=uuid.uuid4().hex,
            project=project,
            nors="Notification",
            date=datetime.datetime.now(),
            response=results
        )

    current_app.db.SentMessages.insert_one(asdict(sentmessage))    
    return render_template("placeholder.html") #render survey + buzz message sent

@pages.route("/send_survey", methods=["GET", "POST"])
def send_survey():
    project = request.form["project"]
    survey_id = request.form["survey"]
    
    
    survey = current_app.db.Surveys.find_one({"_id":survey_id})
    print(survey["questions"])
    questions = current_app.db.Questions.find({"_id": {"$in": survey["questions"]}})
    questionlist = []   
    for question in questions:
        print(question["content"])
        questionlist.append(question["content"])

    contacts = current_app.db.Contacts.find() #update queru to only take project specifc to minimise load
    results = []

    for contact in contacts:
        if contact["project"] == project:
           
            opensurvey = OpenSurvey(
            contact=contact["phone"],
            questions=questionlist)

            
            result = send_message(contact["phone"],questionlist[0])
            current_app.db.OpenSurvey.insert_one(asdict(opensurvey))
            results.append(result)
            

    sentmessage = SentMessage(
            _id=uuid.uuid4().hex,
            project=project,
            nors="Survey",
            date=datetime.datetime.now(),
            response=results
        )

    current_app.db.SentMessages.insert_one(asdict(sentmessage))   
   
    return render_template("placeholder.html") #render survey + buzz message sent

@pages.route("/survey_recieve", methods=['GET','POST'])
def survey_recieve(): 
    #process input and filter
    number = request.values.get("From", "")
    number = number.lstrip("whatsapp:")
    print(number)
    multi = request.values
    print(multi)
    
    incoming_msg = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    msg = resp.message()
    responded = False
    
    #insert the phone number from Twilio
    survey = current_app.db.OpenSurvey.find_one({"contact": number})
    if survey:
        current_app.db.OpenSurvey.update_one({"_id": survey["_id"]}, {"$push": {"responses": incoming_msg}})
        survey = current_app.db.OpenSurvey.find_one({"contact": number})
        opensurvey = OpenSurvey(
            contact=survey["contact"],
            questions=survey["questions"],
            responses=survey["responses"])
        responseNumber = len(survey["responses"])
      
        if len(survey["questions"]) == len(survey["responses"]):
            send_message(survey["contact"],"Thank you for completing the survey. We have Credited your account with 25 shillings")
            current_app.db.CompletedSurvey.insert_one(asdict(opensurvey))
            current_app.db.OpenSurvey.delete_one({"contact": number})
            
        else:
            send_message(survey["contact"],survey["questions"][responseNumber])
            print("message sent")
    else:
        response = chat(incoming_msg)
        current_app.db.BotResponseUnSorted.insert_one({"question":incoming_msg,"label":response[1]})
        send_message(number, response[0])
        


    
 
    

    # what to return?
    return str(msg)

#delete

##USER ENDPOINTS
@pages.route("/register", methods=["GET", "POST"])
def register():
    if session.get("email"):
        return redirect(url_for(".index"))

    form = RegisterForm()

    if form.validate_on_submit():
        user = User(
            _id=uuid.uuid4().hex,
            email=form.email.data,
            password=pbkdf2_sha256.hash(form.password.data),
        )

        current_app.db.Users.insert_one(asdict(user))

        flash("User registered successfully", "success") ## add this everywhere needed

        return redirect(url_for(".login"))

    return render_template(
        "register.html", title="Phoner Marketing - Register", form=form
    )

@pages.route("/login", methods=["GET", "POST"])
def login():
    if session.get("email"):
        return redirect(url_for(".index"))

    form = LoginForm()

    if form.validate_on_submit():
        user_data = current_app.db.Users.find_one({"email": form.email.data})
        if not user_data:
            flash("Login credentials not correct", category="danger")
            return redirect(url_for(".login"))
        user = User(**user_data)

        if user and pbkdf2_sha256.verify(form.password.data, user.password):
            session["user_id"] = user._id
            session["email"] = user.email

            return redirect(url_for(".index"))

        flash("Login credentials not correct", category="danger")

    return render_template("login.html", title="Phoner Marketing - Login", form=form)

@pages.route("/logout", methods=["GET", "POST"])
def logout():
    current_theme = session.get("theme")
    session.clear()
    session["theme"] = current_theme
    return redirect(url_for(".index"))


@pages.route("/")
#@login_required
def index():
   

    return render_template(
        "index.html",
        title="Phoner"
       
    )
###Notification Center
@pages.route("/notification", methods=["GET", "POST"])
def notification():    
    user_data = current_app.db.Users.find_one({"email": session["email"]}) #finds user related SMS questions
    
    user = User(**user_data)

    all_notifications = current_app.db.Notifications.find({"_id": {"$in": user.notifications }})
    
    return render_template("notification.html", notification_data=all_notifications)

@pages.route("/add_notification", methods=["GET", "POST"])
#@login_required
def add_notification():
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
            return redirect(url_for(".notification"))
         
    return render_template("notification_new.html",
    title="Phoner - Create New Notification", form=form)

@pages.get("/notification/<string:_id>")
def notification_details(_id:str):
    
    notification_data = current_app.db.Notifications.find_one({"_id": _id})
    notification = Notification(**notification_data)
    
    #render a form and populate it with information to edit now its just view the information see udemy
    
    return render_template("notification_details.html", notification=notification)

@pages.route("/edit/<string:_id>", methods=["GET", "POST"])
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



@pages.route("/notification/<string:_id>/delete", methods=["GET", "POST"])
#require login
def notification_delete(_id):

    current_app.db.Notifications.delete_one({"_id": _id})


    return redirect(url_for(".notification"))

@pages.get("/notification/<string:_id>/rate")
def notification_rate(_id):
    rating= int(request.args.get("rating"))
    current_app.db.Notifications.update_one({"_id": _id}, {"$set":{"ratingImportance":rating}})

    return redirect(url_for(".notification_details", _id=_id))


@pages.route("/notification/send", methods=["GET", "POST"])
#require login
def notification_send():
    user_data = current_app.db.Users.find_one({"email": session["email"]}) #finds user related SMS questions
    
    user = User(**user_data)


    projects = current_app.db.Contacts.distinct("project")
    
    all_notifications = current_app.db.Notifications.find({"_id": {"$in": user.notifications }})

    
    
    return render_template("notification_send.html", notifications=all_notifications, projects=projects)

@pages.route("/notification/schedule/", methods=["GET", "POST"])
#require login
def notification_schedule():
    user_data = current_app.db.Users.find_one({"email": session["email"]}) #finds user related SMS questions
    
    user = User(**user_data)


    projects = current_app.db.Contacts.distinct("project")
    
    all_notifications = current_app.db.Notifications.find({"_id": {"$in": user.notifications }})
    return render_template("notification_schedule.html", notifications=all_notifications, projects=projects)

###SURVEY

@pages.route("/survey", methods=["GET", "POST"])
def survey():
   
    
    #this requires a session to be created and therefor forces you to login/not ideal and should be updated
    #questions
    user_data = current_app.db.Users.find_one({"email": session["email"]}) #finds user related SMS questions
   
    user = User(**user_data)
    
    question_data = current_app.db.Questions.find({"_id": {"$in": user.questions}})
    survey_data = current_app.db.Surveys.find({"_id": {"$in": user.surveys}})
    
    return render_template(
        "survey.html", survey_data=survey_data, question_data=question_data
    )

@pages.route("/survey_add", methods=["GET", "POST"])
def survey_add():
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

        return redirect(url_for(".survey"))

    return render_template(
        "survey_add.html", title="Add new survey", form=form
    )

@pages.route("/survey_edit/<string:_id>", methods=["GET", "POST"])
def survey_edit(_id:str):
    
    survey_data = current_app.db.Surveys.find_one({"_id": _id})
    
    survey = Survey(**survey_data)
    
    form = SurveyForm(obj=survey)

    if form.validate_on_submit():
        
        survey.title = form.title.data    
        survey.content = form.content.data
        

        

        current_app.db.Surveys.update_one({"_id": survey._id}, {"$set": asdict(survey)})
        return redirect(url_for(".survey_details", _id=survey._id))
    return render_template("survey_form.html", survey=survey, form=form)

@pages.route("/survey_delete/<string:_id>", methods=["GET", "POST"])
def survey_delete(_id:str):
    current_app.db.Surveys.delete_one({"_id": _id})


    return redirect(url_for(".survey"))



@pages.get("/survey/<string:_id>")
def survey_details(_id:str):
    
    survey_data = current_app.db.Surveys.find_one({"_id": _id})
    survey = Survey(**survey_data)

    survey_questions = current_app.db.Questions.find({"_id": {"$in": survey.questions}})
    
    return render_template("survey_details.html", survey=survey, survey_questions=survey_questions)




@pages.route("/survey_question_add/<string:_id>/", methods=["GET", "POST"])
#require login
def survey_question_add(_id:str):
   
    user_data = current_app.db.Users.find_one({"email": session["email"]}) 
   
    user = User(**user_data)
    
    question_data = current_app.db.Questions.find({"_id": {"$in": user.questions}})


    survey_data = current_app.db.Surveys.find_one({"_id": _id})
    survey = Survey(**survey_data)


    return render_template("survey_question_add.html", survey=survey, question_data=question_data)

##add new survey question
@pages.route("/survey_question_add/<string:_id>/<string:q_id>/", methods=["GET", "POST"])
#require login
def survey_question_addq(_id:str, q_id:str):
    

    current_app.db.Surveys.update_one(    {"_id": _id}, {"$push": {"questions": q_id}})
    

    user_data = current_app.db.Users.find_one({"email": session["email"]}) 
   
    user = User(**user_data)
    
    question_data = current_app.db.Questions.find({"_id": {"$in": user.questions}})


    survey_data = current_app.db.Surveys.find_one({"_id": _id})
    survey = Survey(**survey_data)


    return redirect(url_for(".survey_details", _id=_id))

@pages.route("/survey_question/<string:_id>/<string:q_id>/remove", methods=["GET", "POST"])
#require login
def survey_question_remove(_id, q_id):

    
    current_app.db.Surveys.update_one({'_id': _id, },
                            { '$pull': { "questions": q_id }})

    return redirect(url_for(".survey_details", _id=_id))


@pages.route("/schedule/", methods=["GET", "POST"])
#require login
def schedule():
    if request.method == 'POST':
        
        

        sm = ScheduledMessage(
            _id=uuid.uuid4().hex,
            project = request.form["project"],
            messageTitle = request.form["messageTitle"],
            #time = request.form["time"],
            date = request.form["date"],
            nors = request.form["nors"],
        )
        

        current_app.db.ScheduledMessage.insert_one(asdict(sm))
        
    
    #return render_template("scheduled_messages.html", scheduled_data=scheduled_data)
    return redirect(url_for(".scheduled_messages"))

@pages.route("/schedule/<string:_id>/delete", methods=["GET", "POST"])
#require login
def schedule_delete(_id):
    current_app.db.ScheduledMessage.delete_one({"_id": _id})


    return redirect(url_for(".scheduled_messages"))

    


@pages.route("/add_notificsation/", methods=["GET", "POST"])
@login_required
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
            return redirect(url_for(".notification"))
         
    return render_template("notification_new.html",
    title="Phoner - Create New Notification", form=form)


@pages.route("/survey/send", methods=["GET", "POST"])
#require login
def survey_send():
    user_data = current_app.db.Users.find_one({"email": session["email"]}) #finds user related SMS questions
    
    user = User(**user_data)


    projects = current_app.db.Contacts.distinct("project")
    
    all_surveys = current_app.db.Surveys.find({"_id": {"$in": user.surveys }})


    
    return render_template("survey_send.html", surveys=all_surveys, projects=projects)

@pages.route("/survey/schedule", methods=["GET", "POST"])
#require login
def survey_schedule():
    user_data = current_app.db.Users.find_one({"email": session["email"]}) #finds user related SMS questions
    
    user = User(**user_data)


    projects = current_app.db.Contacts.distinct("project")
    
    all_surveys = current_app.db.Surveys.find({"_id": {"$in": user.surveys }})
    return render_template("survey_schedule.html", surveys=all_surveys, projects=projects)



## question
@pages.route("/question_add", methods=["GET", "POST"])
def question_add():
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

        return redirect(url_for(".survey"))

    return render_template(
        "question_add.html", title="Add new question", form=form
    )

    

#question details
@pages.get("/question/<string:_id>")
def question_details(_id:str):
    
    question_data = current_app.db.Questions.find_one({"_id": _id})
    question = Question(**question_data)
    
    #render a form and populate it with information to edit now its just view the information see udemy
    
    return render_template("question_details.html", question=question)

@pages.route("/question_edit/<string:_id>", methods=["GET", "POST"])
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



@pages.route("/question/<string:_id>/delete", methods=["GET", "POST"])
#require login
def question_delete(_id):

    current_app.db.Questions.delete_one({"_id": _id})


    return redirect(url_for(".survey"))


@pages.route("/contacts_update/", methods=["GET", "POST"])
#require login
def contacts_update():
    #INSERT METhOD tHAT CALLS DB HERE. 
    #url = "https://app.buymore.co.ke/"
    #project_owner = "4Life"
    #password = "fakePassword"
    #response = requests.get(url, project_owner, password)
    #response.json()

    contacts = current_app.db.Contacts.find({})
    
    contact = Contact("4","Michael", "Christensen","Bidi Bidi", "+4542345741")

    current_app.db.Contacts.insert_one(asdict(contact))
    #all_sms = [SMS(**sms) for sms in sms_db_content]
    return contacts

@pages.route("/contacts_get/", methods=["GET", "POST"])
#require login
def contacts_get():
    contacts = current_app.db.Contacts.find({})
    #sms_db_content = current_app.db.Questions.find({}) #remember to update questions to the proper database
    all_contacts = [Contact(**x) for x in contacts]
    
    return all_contacts


## pull new contacts
## merge contacts
## display contacts

@pages.route("/dataroom", methods=["GET", "POST"])
def dataroom():
    sentList = [13,12,24,17,45,30]
    sentmessages = current_app.db.SentMessages.find({})
    results = {}
    current_time = datetime.datetime.now()
    for i in range(7):
  # Calculate the date of the current day
        date = current_time - datetime.timedelta(days=i)
    
        results[date.date()] = 0
        
        
        for message in sentmessages:
            print(date.date())
            print("-")
            print(message["date"].date())
            print("ENDOFSTORY")
            print(date.date() == message["date"].date())
    # Check if the date of the message matches the date of the current day
            if message["date"].date() == date.date():
      # If it matches, increment the value in the results dictionary
                print("i do the add")
                results[date.date()] += 1

    print(results)

    labels = list(results.keys())
    data = list(results.values())
    for label in labels:
        label = label.strftime("%d")
        print(label)
    print(labels)
    print(data)
    daysList = ["m","t","w","t","f","l","s"]
    return render_template("dataroom.html", labels=labels, data=data)

@pages.route("/scheduled_messages", methods=["GET", "POST"])
def scheduled_messages():
    scheduled_data = current_app.db.ScheduledMessage.find({})   
    #all_schedule = [ScheduledMessage(**x) for x in scheduled_data]
    #print(all_schedule)
    return render_template("scheduled_messages.html", scheduled_data=scheduled_data)
    

@pages.route("/delete_scheduled_messages", methods=["GET", "POST"])
def delete_scheduled_messages():
    #delete the message selected
    #pass remaining list of messages
    return redirect("scheduled_messages.html")

@pages.route("/chatbot", methods=["GET", "POST"])
def chatbot():
    all_unsorted = current_app.db.BotResponseUnSorted.find()

    return render_template(
        "chatbot.html", all_unsorted=all_unsorted
    )

@pages.route("/approve_model/<string:_id>")
def approve_model(_id:str):
    objInstance = ObjectId(_id)
    response = current_app.db.BotResponseUnSorted.find_one( objInstance)
   
    current_app.db.BotResponseSorted.insert_one(response)
    current_app.db.BotResponseUnSorted.delete_one({"_id": objInstance})
    return redirect(url_for(".chatbot"))

@pages.route("/edit_model/<string:_id>")
def edit_model(_id:str):
    objInstance = ObjectId(_id)
    response = current_app.db.BotResponseUnSorted.find_one( objInstance)
    
    return "placeholder for " + response["question"]

# Not needed section
@pages.route("/placeholder", methods=["GET", "POST"])
def placeholder():
    project = request.form["project"]
    message = request.form["survey"]
    
    contacts = current_app.db.Contacts.find() #update queru to only take project specifc to minimise load
    for contact in contacts:
        if contact["project"] == project:
            print(contact["phone"])
            send_message(contact["phone"],message)
    return render_template("placeholder.html")

@pages.get("/sms/<string:_id>")
def sms(_id:str):
    sms_data = current_app.db.Questions.find_one({"_id": _id})
    sms = SMS(**sms_data)
    return render_template("sms_details.html", sms=sms)




@pages.get("/toggle-theme")
def toggle_theme():
    current_theme = session.get("theme")
    if current_theme == "dark":
        session["theme"] = "light"
    else:
        session["theme"] = "dark"

    return redirect(request.args.get("current_page"))

