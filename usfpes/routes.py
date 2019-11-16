import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from usfpes import app,db,bcrypt,mail
from usfpes.models import User
from usfpes.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, PasswordResetForm
from flask_login import current_user,login_user,logout_user,login_required
from flask_mail import Message

@app.route("/")
def index():
    return redirect(url_for('home'))

@app.route("/home")
def home():
    return render_template('home.html',title='Home')


@app.route("/about")
def about():
    return render_template('about.html',title='About')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and/or password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password,student_id=form.student_id.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/logout")
def logout():
    logout_user()
    flash('You have successfully logged out.', 'success')
    return redirect(url_for('home'))

names = ['Procastination Survey',
         'Self Esteem Survey',
         'Ten Item Personality Test']
ques = ['https://www.psytoolkit.org/cgi-bin/psy2.6.1/survey?s=YTJzz',
        'https://www.psytoolkit.org/cgi-bin/psy2.6.1/survey?s=vfQcw',
        'https://www.psytoolkit.org/cgi-bin/psy2.6.1/survey?s=Z2huR']

@app.route("/psyeve/<int:num>",methods=['GET', 'POST'])
@login_required
def psyeve(num):
    if num > len(ques):
        return render_template('errors/404.html'), 404
    if num == len(ques):
        flash('You have successfully filled all the surveys','success')
        current_user.filled_survey = True
        db.session.commit()
        return redirect(url_for('home'))
    if current_user.filled_survey:
        flash('You have already filled all the surveys','info')
        return redirect(url_for('home'))

    return render_template('psy_tests/list_of_tests.html',title='Psychometric Evaluation Portal',ques=ques,names=names,num=num)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path,'static/profile_pics',picture_fn)

    output_size = (125,125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    #form_picture.save(picture_path)
    return picture_fn



@app.route("/account",methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file

        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.student_id = form.student_id.data
        db.session.commit()
        flash('Your account info has been updated!','success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.student_id.data = current_user.student_id

    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file,form=form)

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',sender='usfpes@gmail.com',recipients=[user.email])
    msg.body = f''' To reset your password, visit the following link:
{url_for('reset_token',token=token,_external=True)}

If you did not make this request, please ignore this email and no changes will be made.
'''
    mail.send(msg)

@app.route("/reset_password",methods=['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with the instructions to reset your password','info')
        return redirect(url_for('login'))
    return render_template('reset_request.html',title='Reset Password',form=form)

@app.route("/reset_password/<token>",methods=['GET','POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That token is either invalid or expired.','warning')
        return redirect(url_for('reset_request'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html',title='Reset Password',form=form)
