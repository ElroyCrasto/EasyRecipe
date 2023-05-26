import base64
from .forms import PostUploadForm ,UserRegistraionForm, UserLoginForm, UserdataEditForm, PostEditForm
from flask import request, render_template, redirect, Blueprint, flash, url_for
from flask_login import login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from . import db
from .models import user, post, img
from thefuzz import fuzz,process

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
        flash("Post Sumbitted Successfully","success")
        return redirect("/")
    else:
        return render_template("upload.html",form=form)


@page.route("/post/<Title>")
def display_post(Title):
    _post = post.query.filter_by(TITLE=Title).first()
    if _post:
        _img = img.query.filter_by(PID=_post.PID).first()
        return render_template("showpost.html", img=_img.bufferdata, mimetype=_img.mimetype, post=_post)
    else:
        return "No post with THat id", 404


@page.route("/del_post", methods=["POST"])
def del_post():
    PID = request.form.get("pid")
    del_post = post.query.filter_by(PID=PID,UID=current_user.UID).first()
    if del_post:
        post.query.filter_by(PID=PID).delete()
        img.query.filter_by(PID=PID).delete()
        db.session.commit()
        flash("Post Deleted Successfully","Success")
    else:
        flash("You are not the owner of that Post","error")
    return redirect("/account")


@page.route("/search",methods=["POST"])
def search():
    search = request.form.get("query")
    posts = post.query.filter_by()
    query_results_list = []
    matched_posts = []
    for i in posts:
        query_results_list.append(i.TITLE)
    search_results = process.extract(search, query_results_list, limit=10)
    for title,ratio in search_results:
        Post = post.query.filter_by(TITLE=title).first()
        matched_posts.append(Post)
    return render_template("search.html",posts=matched_posts)

@page.route("/post/edit/<pid>",methods=["GET","POST"])
def edit_profile(pid):
    _post = post.query.filter_by(PID=pid).first()
    if current_user.UID != _post.UID: 
        flash("You are not the Owner of the post")
        redirect("/")
    form = PostEditForm(Post=_post)
    form.desc.data = _post.PD
    form.nutri.data = _post.NUTRI
    form.ing.data = _post.ING 
    form.recipe.data = _post.RECIPE

    if form.validate_on_submit():
        if _post.TITLE != form.title.data:_post.TITLE = form.title.data
        if _post.PD != form.desc.data: _post.PD = _post.desc.data
        if _post.ING != form.ing.data: _post.ING = _post.ing.data
        if _post.NUTRI != form.nutri.data: _post.NUTRI = _post.nutri.data
        if _post.RECIPE != form.recipe.data: _post.RECIPE = form.recipe.data
        db.session.commit()
        if form.img.data:
            db.session.delete(_post.img[0])
            db.session.commit()
            pic = form.img.data
            bufferdata=base64.b64encode(pic.read()).decode('utf-8')
            new_img = img(NAME=secure_filename(pic.filename),
                      bufferdata=bufferdata,
                      mimetype=pic.mimetype,
                      PID=_post.PID)
            db.session.add(new_img)
            db.session.commit()
        flash("Post Updated Successfully", "success")
        return redirect("/account")
    if form.errors != {}:
        for error in form.errors.values():
            flash(error[0],"error")
    return render_template("editpost.html",form=form)