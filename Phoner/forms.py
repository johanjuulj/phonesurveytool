from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField, PasswordField, TextAreaField, SelectField
from wtforms.validators import InputRequired, Email, Length, EqualTo

class NotificationForm(FlaskForm):
    title = StringField("Title", validators=[InputRequired()])
    content = TextAreaField("Message Content", validators=[InputRequired()])
    submit = SubmitField("Add Notification")

class UpdateContacts(FlaskForm):
    ASSET_UID = StringField("Asset UID for Survey", validators=[InputRequired()])
    update_type = SelectField("OverwriteAdd", choices=["Overwrite (based on phonenumber)", "Add All"])
    note = TextAreaField("Note for Update", validators=[InputRequired()])
    submit = SubmitField("Update Contacts")

# class NotificationSendForm(FlaskForm):
#     notificationTitle =StringField("Notification Title", validators=[InputRequired()])
#     recipientProject = StringField("Recipient Project", validators=[InputRequired()])

class SendForm(FlaskForm):
    message = SelectField('What message do you want to send?')
    age = SelectField('Filter by age group:    ', choices=[('none', 'None'),('0-18', '0-18'), ('19-30', '19-30'), ('31-50', '31-50'), ('51+', '51+')],default='none')
    gender = SelectField('Filter by gender', choices=[('none', 'None'), ('female', 'Female'), ('male', 'Male'), ('other', 'Other')], default='none')
    kids = SelectField('Filter by number of kids', choices=[('none', 'None'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5+', '5+')], default='none')
    education = SelectField('Filter by educatio', choices=[('none', 'None'), ('primary', 'Primary'), ('secondary', 'Secondary'), ('university', 'University')], default='none')
    village = SelectField('Filter by village', default='none')
    submit = SubmitField("Send message")

    def __init__(self, messages=None, villages=None, *args, **kwargs):
        super(SendForm, self).__init__(*args, **kwargs)
        self.message.choices = [(msg['title'], msg['title']) for msg in messages]
        self.village.choices = villages

#class SendForm(FlaskForm):
#    message = SelectField("What do you want to send?", validators=[InputRequired()])
#    age = SelectField("What age groupt", validators=[InputRequired()])
#    age = SelectField("What age groupt", validators=[InputRequired()])
#    submit = SubmitField("Add Question")

class QuestionForm(FlaskForm):
    title = StringField("Title", validators=[InputRequired()])
    content = StringField("Question Content", validators=[InputRequired()])
    submit = SubmitField("Add Question")

class SurveyForm(FlaskForm):
    title = StringField("Title", validators=[InputRequired()])
    content = StringField("Survey Content", validators=[InputRequired()])
    submit = SubmitField("Add Survey")



class RegisterForm(FlaskForm):
    email = StringField("Email", validators = [InputRequired(),Email()])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=8, message="Your password must be atleast 8 characters long")])
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            InputRequired(),
            EqualTo(
                "password",
                message="This password did not match the one in the password field.",
            ),
        ],
    )

    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")


#typically returns a string but this class changes the TextAreaField to become alist of strings
class StringListField(TextAreaField):
    def _value(self):
        if self.data:
            return "\n".join(self.data)
        return ""

    def process_formdata(self, valuelist):
        if valuelist and valuelist[0]:
            self.data = [line.strip() for line in valuelist[0].split("\n")]
        else:
            self.data = []

class ExtendedNotificationForm(NotificationForm):
    comment = StringListField("Comments")
    status = SelectField("Status", choices=["Draft", "Approved"])
    submit = SubmitField("Submit")
