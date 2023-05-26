import base64
from .forms import PostUploadForm ,UserRegistraionForm, UserLoginForm, UserdataEditForm
from flask import request, render_template, redirect, Blueprint, flash, url_for
from flask_login import login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from . import db
from .models import user, post, img

account = Blueprint("account", __name__,)


@account.route("/register", methods=["POST", "GET"])
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
        return redirect(url_for("account.register"))
    return render_template("register.html", form=form)


@account.route("/login", methods=["POST", "GET"])
def login():
    form = UserLoginForm()
    if form.validate_on_submit():
        login_user(form.user, remember=True)
        return redirect("/")
    if form.errors != {}:
        for error in form.errors.values():
            flash(error[0],"error")
    return render_template("login.html",form=form)


@login_required
@account.route("/account")
def user_profile():
    return render_template("account.html",user=current_user)


@login_required
@account.route("/profile/edit",methods=["GET","POST"])
def edit_profile():
    form = UserdataEditForm(user=current_user)
    if form.validate_on_submit():
        current_user.USERNAME = form.username.data
        current_user.EMAIL = form.email.data
        Logout = False
        print(form.password2.data)
        if form.password2.data != "":
            current_user.PASSWORD = generate_password_hash(form.password2.data)
            Logout = True
        db.session.commit()
        flash("Profile Updated Successfully", "success")
        if Logout:
            return redirect("/logout")
        return redirect("/profile/edit")
    if form.errors != {}:
        for error in form.errors.values():
            flash(error[0],"error")
    return render_template("editProfile.html",form=form)


@login_required
@account.route("/logout")
def logout():
    logout_user()
    return redirect("/")


@account.route("/profile/<username>")
def  view_profile(username):
    print(current_user)
    if not current_user.is_anonymous:
        if current_user.USERNAME == username:
            return redirect("/account")
    User = user.query.filter_by(USERNAME=username).first()
    if User:
        return render_template("user_posts.html",user=User)
    flash("No such User found","error")
    return redirect("/")