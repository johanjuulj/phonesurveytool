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
import pandas as pd

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
        if message["date"] == message["date"]: #match date check same y m d format - is there a better way than cronjob to check?
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

    #set a state/user variable for which platform to use whatsapp or sms
    platform = "whatsapp"
    message = client.messages.create( 
                              from_=f'{platform}:+14155238886',  
                              body=f'{_message}',      
                              to=f'{platform}:{number}' 
                          ) 
    sentmessage = SentMessage(
            _id=uuid.uuid4().hex,
            project=number,
            date=datetime.datetime.now(),
            response=message.sid #store more meaningfull input 
        )
   
    current_app.db.SentMessages.insert_one(asdict(sentmessage)) 
    
    return message.sid


def login_required(route):  
    @functools.wraps(route)  #function that replaces any end-point and runs a login check
    def route_wrapper(*args, **kwargs):
        if session.get("email") is None:
            return redirect(url_for(".login"))

        return route(*args, **kwargs)

    return route_wrapper

@pages.route("/")

def index():
   

    return render_template(
        "index.html",
        title="Phoner"
       
    )



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

        flash("User registered successfully", "success") 
    

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



##SEND AND RECIEVE ENDPOINTS




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


####### API Contact calls

@pages.route("/contacts")
def contacts():
    contacts = current_app.db.Contacts.find({})
    #sms_db_content = current_app.db.Questions.find({}) #remember to update questions to the proper database
    all_contacts = [Contact(**x) for x in contacts]
    
    return render_template("contacts.html", all_contacts=all_contacts)


@pages.route("/contacts_update/", methods=["GET", "POST"])
#require login
def contacts_update():
    #INSERT METhOD tHAT CALLS DB HERE. 
    TOKEN = 'fca5c203b64e9ebc661d0154fe430f5918d0f6a4' #account token: in kobo go to account->settings
    KF_URL = 'kobo.humanitarianresponse.info' #or 'kf.kobotoolbox.org'
    ASSET_UID = 'afS4VYAKGa25JCqigdiCKv' #asset id of the project gotten from the url e.g. https://kobo.humanitarianresponse.info/#/forms/axXYMX67noGAR9i4HNNMUR/summary - TOOL specifc
    QUERY = '{"start":{"$gt":"2022-10-10"}}' # query for filtering results  https://www.mongodb.com/docs/manual/reference/operator/query/#query-selectors
    #URL = f'https://{KF_URL}/api/v2/assets/{ASSET_UID}/data/?query={QUERY}&format=json' # use when using query
    URL = f'https://{KF_URL}/api/v2/assets/{ASSET_UID}/data/?format=json'
    headers = {"Authorization": f'Token {TOKEN}'}


    response = requests.get(URL, headers=headers) #kobo API call
    data = response.json()
    df = pd.DataFrame(data['results'])
    
    for index, row in df.iterrows():
    # Access the values of each column
        name = row.get('End_users_first_name_and_last_name')
        phone = row.get('Phone_number')
        gender = row.get('Gender')
        age = row.get('Age')
        kids = row.get('Number_of_kids')
        education = row.get('Education')
        village = row.get('Village')

        
    
    # Create a dictionary to represent the document
        document = {
        'name': name,
        'phone': phone,
        'gender': gender,
        'age': age,
        'kids': kids,
        'education': education,
        'village': village
    }
        
    
    

    #contacts = current_app.db.Contacts.find({})
    
    #contact = Contact("4","Michael", "Christensen","Bidi Bidi", "+4542345741")

    current_app.db.Contacts.insert_one(document)
    print(document)
    #all_sms = [SMS(**sms) for sms in sms_db_content]
    return redirect(url_for(".contacts"))

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



####### Dataroom

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
    daysList = ["m","t","w","tSettings","f","l","s"]
    return render_template("dataroom.html", labels=labels, data=data)





########## Chatbot
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

#####
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




@pages.get("/toggle-theme")
def toggle_theme():
    current_theme = session.get("theme")
    if current_theme == "dark":
        session["theme"] = "light"
    else:
        session["theme"] = "dark"

    return redirect(request.args.get("current_page"))

