from flask_wtf import FlaskForm
from werkzeug.security import check_password_hash
from wtforms import StringField, TextAreaField, EmailField, PasswordField, SubmitField,SelectField
from flask_wtf.file import FileField, FileAllowed,FileRequired
from wtforms.validators import InputRequired, EqualTo, Length, DataRequired, Email, ValidationError, Optional
from .models import user, post, img
import base64

class UserRegistraionForm(FlaskForm):

    def validate_username(self, input):
        username = user.query.filter_by(USERNAME=str(input.data)).first()
        if username:
            raise ValidationError("This Username is already in Use")

    def validate_email(self, input):
        email = user.query.filter_by(EMAIL=str(input.data)).first()
        if email:
            raise ValidationError("This email is already in Use")

    username = StringField(label="Username", validators=[Length(min=6), InputRequired()])
    email = EmailField(label="Email", validators=[Email(), InputRequired()])
    password1 = PasswordField(label="Password", validators=[Length(min=6), InputRequired()])
    password2 = PasswordField(label="Confirm Password", validators=[EqualTo("password1","Passwords Do Not Match")])
    submit = SubmitField(label="Create Account")


class UserLoginForm(FlaskForm):

    def validate(self, extra_validators=None):
        initial_validation = super(UserLoginForm, self).validate()
        if not initial_validation:
            return False
        User = user.query.filter_by(USERNAME=self.username.data).first()
        if User is None:
            self.username.errors.append("User with this Username Does not Exist")
            return False

        if not check_password_hash(User.PASSWORD, self.password.data):               
            self.password.errors.append("Incorrecnt Password")
            return False
        self.user = User
        return True

    username = StringField(label="Username")
    password = PasswordField(label="Password")
    submit = SubmitField(label="Login")


class PostUploadForm(FlaskForm):
    title = StringField(label="Title",validators=[InputRequired(message="Title Is Required")])
    img = FileField(label="Upload Thumbnail",
     validators=[FileRequired(message="A Thumnail is Required"),
            FileAllowed(["jpg", "jpeg", "jfif", "pjpeg", "pjp", "png"],
            message="Please Upload only Images.(.png,.jpg,jpeg)")])
    desc = StringField(label="Description",validators=[InputRequired(message="Description is Required")])
    ing = TextAreaField(label="Ingredients")
    nutri = TextAreaField(label="Nutrition")
    recipe = TextAreaField(label="Preparation Steps")
    submit = SubmitField(label="Post")


class UserdataEditForm(FlaskForm):

    def __init__(self, user):
        super().__init__()
        self.user = user
        

    def validate_username(self, input):
        if input.data != self.user.USERNAME:
            if user.query.filter_by(USERNAME=input.data).first():
                raise ValidationError("Username Already In Use")
            
    def validate_email(self,input):
        if input.data != self.user.EMAIL:
            if user.query.filter_by(EMAIL=input.data).first():
                raise ValidationError("Email Already in Use")

    def validate_oldPassword(self,input):
        if not check_password_hash(self.user.PASSWORD, input.data):
            raise ValidationError("Incorrect Password")

    username = StringField(label="Username", validators=[Length(min=6), InputRequired()])
    email = EmailField(label="Email", validators=[Email(), InputRequired()])
    oldPassword = PasswordField(label="Current Password",validators=[InputRequired()])
    password1 = PasswordField(label="Password", validators=[Length(min=6), Optional()])
    password2 = PasswordField(label="Confirm Password", validators=[EqualTo("password1","Passwords Do Not Match")])
    submit = SubmitField(label="Save")

class PostEditForm(FlaskForm):

    def __init__(self, Post):
        super().__init__()
        self.Post = Post

    def validate_title(self, input):
        if input.data.strip() != self.Post.TITLE:
            title_check = post.query.filter_by(TITLE=input.data.strip()).first()
            if title_check:
                raise ValidationError("Title already in use")


    title = StringField(label="Title", validators=[InputRequired(message="Title Is Required")])
    img = FileField(label="Upload Thumbnail",
     validators=[FileAllowed(["jpg", "jpeg", "jfif", "pjpeg", "pjp", "png"],
            message="Please Upload only Images.(.png,.jpg,jpeg)"), Optional()])
    desc = StringField(label="Description", validators=[InputRequired(message="Description is Required")])
    ing = TextAreaField(label="Ingredients")
    nutri = TextAreaField(label="Nutrition")
    recipe = TextAreaField(label="Preparation Steps")
    submit = SubmitField(label="Post")
