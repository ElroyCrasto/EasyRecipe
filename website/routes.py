import base64
from .forms import PostUploadForm ,UserRegistraionForm, UserLoginForm
from flask import request, render_template, redirect, Blueprint, flash, url_for
from flask_login import login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from . import db
from .models import user, post, img

page = Blueprint("page", __name__)


@page.route('/')
def hello_world():
    return render_template("homepage.html")


@page.before_request
def run():
    db.create_all()
    db.session.commit()


@page.route('/upload', methods=["POST", "GET"])
@login_required
def upload():
    form = PostUploadForm()
    if form.validate_on_submit():
        pic = form.img.data
        new_post = post(form.title.data, form.desc.data, form.ing.data, form.nutri.data, form.recipe.data, current_user.UID)
        db.session.add(new_post)
        db.session.commit()
        new_img = img(secure_filename(pic.filename),
                      base64.b64encode(pic.read()).decode('utf-8'),
                      mimetype=pic.mimetype,
                      PID=new_post.PID)
        db.session.add(new_img)
        db.session.commit()
        return redirect("/")
    else:
        return render_template("upload.html",form=form)


@page.route("/login", methods=["POST", "GET"])
def login():
    form = UserLoginForm()
    if form.validate_on_submit():
        login_user(form.user, remember=True)
        return redirect("/")
    if form.errors != {}:
        for error in form.errors.values():
            flash(error[0],"error")
    return render_template("login.html",form=form)


@page.route("/register", methods=["POST", "GET"])
def register():
    form = UserRegistraionForm()
    if form.validate_on_submit():
        new_user = user(form.username.data,
         generate_password_hash(form.password2.data, method="sha256"),
          form.email.data)
        db.session.add(new_user)
        db.session.commit()
        flash("User Successfully Created","success")
        return redirect("/login")
    if form.errors != {}:
        for error in form.errors.values():
            flash(error[0],"error")
        return redirect(url_for("page.register"))
    return render_template("register.html", form=form)


@login_required
@page.route("/logout")
def logout():
    logout_user()
    return redirect("/")


@page.route("/post/<Title>")
def display_post(Title):
    _post = post.query.filter_by(TITLE=Title).first()
    if _post:
        _img = img.query.filter_by(PID=_post.PID).first()
        return render_template("showpost.html", img=_img.bufferdata, mimetype=_img.mimetype, post=_post)
    else:
        return "No post with THat id", 404

@login_required
@page.route("/account")
def user_profile():
    return render_template("account.html",user=current_user)


@page.route("/profile/<username>")
def  view_profile(username):
    if current_user.USERNAME == username:
        return redirect(url_for("user_profile.html"))
    User = user.query.filter_by(USERNAME=username).first()
    if User:
        return render_template("user_posts.html",user=User)
    flash("No such User found","error")
    return render_template("/")

@page.route("/del_post/<PID>", methods=["POST"])
def del_post(PID):
    del_post = post.query.filter_by(PID=PID).first()
    if del_post.UID == current_user.UID:
        post.query.filter_by(PID=PID).delete()
        db.session.commit()
    else:
        flash("You are not the owner of that Post","error")
    return redirect("/account")
