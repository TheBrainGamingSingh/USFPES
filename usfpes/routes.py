import os
import secrets
from datetime import timedelta
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from usfpes import app,db,bcrypt,mail
from usfpes.models import User,Responses
from usfpes.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, PasswordResetForm,SurveyForm
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
            delta = timedelta(minutes=15)
            login_user(user, remember=form.remember.data,duration=delta)
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
        send_welcome_email(user)
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/logout")
def logout():
    logout_user()
    flash('You have successfully logged out.', 'success')
    return redirect(url_for('home'))

names = ['Social Intelligence',
         'Procrastination',
         'Cognition',
         'Self Esteem Survey',
         'Cognitive Flexibility',
         'Narcissism',
         'Social Media',
         'Internet Usage',
         'Loneliness',
         'Ten Item Personality Test',
         'Risk Taking',
         'Flourishing Scale']
ques = ['https://www.psytoolkit.org/cgi-bin/psy2.6.1/survey?s=gCtsv',
        'https://www.psytoolkit.org/cgi-bin/psy2.6.1/survey?s=YTJzz',
        'https://www.psytoolkit.org/cgi-bin/psy2.6.1/survey?s=MJEWG',
        'https://www.psytoolkit.org/cgi-bin/psy2.6.1/survey?s=vfQcw',
        'https://www.psytoolkit.org/cgi-bin/psy2.6.1/survey?s=4c9jf',
        'https://www.psytoolkit.org/cgi-bin/psy2.6.1/survey?s=JuVjm',
        'https://www.psytoolkit.org/cgi-bin/psy2.6.1/survey?s=rbc2T',
        'https://www.psytoolkit.org/cgi-bin/psy2.6.1/survey?s=Lc8xQ',
        'https://www.psytoolkit.org/cgi-bin/psy2.6.1/survey?s=QHKsK',
        'https://www.psytoolkit.org/cgi-bin/psy2.6.1/survey?s=Z2huR',
        'https://www.psytoolkit.org/cgi-bin/psy2.6.1/survey?s=jJZ43',
        'https://www.psytoolkit.org/cgi-bin/psy2.6.1/survey?s=fuMBR']

@app.route("/psyeve/<int:num>",methods=['GET', 'POST'])
@login_required
def psyeve(num):
    if current_user.filled_survey:
        flash('You have already filled all the surveys','info')
        return redirect(url_for('home'))
    if num != current_user.last_filled:
        return redirect(url_for('psyeve',num=current_user.last_filled))
        #return render_template('psy_tests/list_of_tests.html',title='Psychometric Evaluation Portal',ques=ques,names=names,num=current_user.last_filled)
    if num > len(ques):
        return render_template('errors/404.html'), 404
    if num == len(ques):
        flash('You have successfully filled all the surveys','success')
        current_user.filled_survey = True
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('psy_tests/list_of_tests.html',title='Psychometric Evaluation Portal',ques=ques,names=names,num=num)


@app.route("/psyeve/success",methods=['GET', 'POST'])
@login_required
def psyevesuccess():
    flash('Survey filled succesfully.','success')
    current_user.last_filled = current_user.last_filled + 1
    db.session.commit()
    return redirect(url_for('psyeve',num=current_user.last_filled))

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

def send_welcome_email(user):
    msg = Message('Unified Student Feedback and Psychometric Evaluation System',sender='usfpes@gmail.com',recipients=[user.email])
    msg.body = f'''You have succesfully registered for Unified Student Feedback and Psychometric Evaluation System.

Your username is {user.username}.
Student ID associated with the username is {user.student_id}.
'''
    mail.send(msg)

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


@app.route('/survey', methods=['GET', 'POST'])
@login_required
def survey():
    form = SurveyForm()
    if form.validate_on_submit():
        response = Responses(course_name=form.course_name.data,course_id=form.course_id.data,faculty_name=form.faculty_name.data,dept=form.dept.data,q1=form.q1.data,q2=form.q2.data,q3=form.q3.data,q4=form.q4.data,q5=form.q5.data,q6=form.q6.data,q7=form.q7.data,q8=form.q8.data,q9=form.q9.data,q10=form.q10.data,q11=form.q11.data,q12=form.q12.data,comments=form.text_area.data)
        db.session.add(response)
        db.session.commit()
        flash(f"Feedback submitted succesfully for Faculty:{form.faculty_name.data}, for the course {form.course_id.data}:{form.course_name.data}!", 'success')
        return redirect(url_for('home'))
    return render_template('survey.html', title='Student Survey', form=form)
