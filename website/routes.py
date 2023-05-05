import base64

from flask import request, render_template, redirect, Blueprint
from flask_login import login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from . import db
from .models import user, post, img

page = Blueprint("page", __name__)


@page.route('/')
def hello_world():
    return 'Hello World!'


@page.before_request
def run():
    db.create_all()
    db.session.commit()


@page.route('/upload', methods=["POST", "GET"])
@login_required
def upload():
    if request.method == "POST":
        pic = request.files["img"]
        title = request.form["title"].strip()
        desc = request.form["desc"].strip()
        ing = request.form["ing"]
        nutri = request.form["nutri"]
        recipe = request.form["recipe"]

        new_post = post(title, desc, ing, nutri, recipe, current_user.UID)
        new_img = img(secure_filename(pic.filename),
                      base64.b64encode(pic.read()).decode('utf-8'),
                      mimetype=pic.mimetype)
        db.session.add(new_img)
        db.session.add(new_post)
        db.session.commit()
        return redirect("/")
    else:
        return render_template("upload.html")


@page.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form.get("nm")
        password = request.form.get("pass")

        check = user.query.filter_by(USERNAME=username).first()
        if check is not None and check_password_hash(check.PASSWORD, password):
            login_user(check, remember=True)
            return redirect("/")
    return render_template("login.html")


@page.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        username = request.form.get('nm')
        password = request.form.get('pass')
        email = request.form.get('email')
        name_check = user.query.filter_by(USERNAME=username).first()
        email_check = user.query.filter_by(EMAIL=email).first()
        if name_check is None and email_check is None:
            new_user = user(username, generate_password_hash(password, method="sha256"), email)
            db.session.add(new_user)
            db.session.commit()
            return redirect("/")
        return redirect("/register"), 400
    else:
        return render_template("register.html")


@login_required
@page.route("/logout")
def logout():
    logout_user()
    return redirect("/")


@page.route("/post/<int:_id>")
def display_post(_id):
    _img = img.query.filter_by(IID=_id).first()
    _post = post.query.filter_by(PID=_id).first()
    if _img is None:
        return "No IMg with THat id", 404
    else:
        return render_template("showpost.html", img=_img.bufferdata, mimetype=_img.mimetype, post=_post)
