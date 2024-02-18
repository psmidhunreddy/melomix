from flask import Blueprint, Flask, request, redirect, url_for, flash, session
from flask import render_template
from . import db
from .models import User,Admin,Creator
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import datetime,pytz
from werkzeug.utils import secure_filename
import os
auth = Blueprint('auth', __name__)

def allow_file(filename):
    ALLOWED_EXTENSION = {'png', 'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSION

@auth.route("/",methods=['GET','POST'])
def home():
    return render_template('userlogin.html')

@auth.route("/admin-login",methods=['GET','POST'])
def admin():
    if request.method=='POST':
        input_username=request.form.get("username")
        input_password=request.form.get("password")
        admin=Admin.query.filter(Admin.username==input_username).first()
        if admin:
            if admin.password==input_password:
                session['user_type'] = 'admin'
                login_user(admin, remember=True)
                return redirect(url_for('home_views.adminhome'))
            else:
                flash("Password is incorrect!", category='error')
        else:
            flash('credentials wrong. There can be only one ADMIN',category='error')
    return render_template('adminlogin.html')



@auth.route("/user-login", methods=['GET', 'POST'])
def user():
    if request.method == 'POST':
        input_email = request.form.get("email")
        input_password = request.form.get("password")
        user = User.query.filter(User.email==input_email).first()
        if user:
            if check_password_hash(user.password, input_password):
                flash("Logged in!", category='success')
                session['user_type'] = 'user'
                login_user(user, remember=True)
                return redirect(url_for('home_views.userhome'))
            else:
                flash("Password is incorrect!", category='error')
        else:
            flash('Email does not exist!', category='error')
    return render_template('userlogin.html', user=current_user)

@auth.route('/log-out',methods=['GET'])
@login_required
def sign_out():
    user = current_user
    user.authenticated = False
    logout_user()
    return redirect("/")

@auth.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        input_email = request.form.get("email")
        input_username = request.form.get("username")
        input_password = request.form.get("password")
        input_confirm_password = request.form.get("confirm_password")

        email_exists = User.query.filter(User.email==input_email).first()
        username_exists = User.query.filter(User.username==input_username).first()
        
        if email_exists:
            flash('Email is already registered with us. Try to login', category='error')
        elif username_exists:
            flash('Username is already registered with us. Try to use different username', category='error')
        elif input_password != input_confirm_password:
            flash('Password don\'t match! ', category='error')
        elif len(input_username) < 2:
            flash('Username length should be atleast 2', category='error')
        elif len(input_password) < 6:
            flash('Password length should be atleast 6', category='error')
        elif len(input_email) < 4:
            flash('Email address is invalid', category='error')
        else:
            new_user = User(email=input_email, username=input_username, password=generate_password_hash(input_password),doc=datetime.datetime.now(pytz.timezone('Asia/Kolkata')))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('User account has been successfully created','success')
            return render_template('userlogin.html', user=current_user)
    return render_template('register.html',user=current_user)

@auth.route("/register-creator", methods=['GET', 'POST'])
@login_required
def creator():
    user=current_user
    cid_exists= Creator.query.filter(Creator.uid==user.id).first()
    if cid_exists:
        return redirect(url_for('home_views.creatorprofile')) 
    if request.method == "POST":
        input_cname=request.form.get("cname")
        input_password=request.form.get("cpassword")
        input_photo=request.files["photo"]
        cname_exists = Creator.query.filter(Creator.cname==input_cname).first()
        if cname_exists:
            flash('Creator name already exists. Try a diff one', category='error')
        else:
            user = current_user
            if check_password_hash(user.password, input_password):
                new_creator=Creator(cname=input_cname,uid=user.id,doc=datetime.datetime.now(pytz.timezone('Asia/Kolkata')))
                db.session.add(new_creator)
                db.session.commit()
                if input_photo and  allow_file(input_photo.filename):
                    filename="creator_"+str(new_creator.id)+"profilephoto"+secure_filename(input_photo.filename)
                    input_photo.save(os.path.join(auth.root_path, 'static/profile_photos/', filename))
                    input_url = "/static/profile_photos/" + filename
                    new_creator.profile_photo=input_url
                    db.session.commit()
                flash("Registered successfull! Wating for admin approval", category='success')
                return redirect(url_for('home_views.creatorprofile'))
            else:
                flash("Password is incorrect!", category='error')
    return render_template("creatorRegistor.html",user=user,creator=cid_exists)