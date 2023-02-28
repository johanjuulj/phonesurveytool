from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField, PasswordField, TextAreaField, SelectField
from wtforms.validators import InputRequired, Email, Length, EqualTo

class NotificationForm(FlaskForm):
    title = StringField("Title", validators=[InputRequired()])
    content = TextAreaField("Message Content", validators=[InputRequired()])
    submit = SubmitField("Add Notification")

# class NotificationSendForm(FlaskForm):
#     notificationTitle =StringField("Notification Title", validators=[InputRequired()])
#     recipientProject = StringField("Recipient Project", validators=[InputRequired()])


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
