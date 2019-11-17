from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField,RadioField,TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from usfpes.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(),Length(min=8, max=20)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    student_id = StringField('Student ID',
                           validators=[DataRequired(), Length(min=8, max=8)])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

    def validate_student_id(self, student_id):
        user = User.query.filter_by(student_id=student_id.data).first()
        if user:
            raise ValidationError('That student ID is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    student_id = StringField('Student ID',
                           validators=[DataRequired(), Length(min=8, max=8)])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

    def validate_student_id(self, student_id):
        if student_id.data != current_user.student_id:
            user = User.query.filter_by(student_id=student_id.data).first()
            if user:
                raise ValidationError('That student ID is taken. Please choose a different one.')

class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])

    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('That email is not associated with any account. Try a different one or Register.')

class PasswordResetForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(),Length(min=8, max=20)])
    confirm_password = PasswordField('Confirm Password',
                                 validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class SurveyForm(FlaskForm):
    course_name = StringField('Course Name', validators=[DataRequired()])

    course_id = StringField('Course ID', validators=[DataRequired()])

    faculty_name = StringField('Faculty Name', validators=[DataRequired()])

    dept = StringField('Department', validators=[DataRequired()])

    q1 = RadioField('Sufficient weightage was given to practicals and assignments', choices=[
        ('0', 'Poor'),
        ('1', 'Average'),
        ('2', 'Good'),
        ('3', 'Very Good'),
        ('4', 'Excellent')
    ], validators=[DataRequired()])

    q2 = RadioField('Organisation of course into lectures and practicals', choices=[
        ('0', 'Poor'),
        ('1', 'Average'),
        ('2', 'Good'),
        ('3', 'Very Good'),
        ('4', 'Excellent')
    ], validators=[DataRequired()])

    q3 = RadioField('The contents of this course are up to date', choices=[
        ('4', 'Completely Agree'),
        ('3', 'Agree'),
        ('2', 'Neutral'),
        ('1', 'Disagree'),
        ('0', 'Completely Disagree')
    ], validators=[DataRequired()])

    q4 = RadioField('This course is important for this degree or programme', choices=[
        ('4', 'Completely Agree'),
        ('3', 'Agree'),
        ('2', 'Neutral'),
        ('1', 'Disagree'),
        ('0', 'Completely Disagree')
    ], validators=[DataRequired()])

    q5 = RadioField('Instructor was punctual and classes were held regularly', choices=[
        ('4', 'Completely Agree'),
        ('3', 'Agree'),
        ('2', 'Neutral'),
        ('1', 'Disagree'),
        ('0', 'Completely Disagree')
    ], validators=[DataRequired()])

    q6 = RadioField('Instructor had sufficient knowledge of course', choices=[
        ('4', 'Completely Agree'),
        ('3', 'Agree'),
        ('2', 'Neutral'),
        ('1', 'Disagree'),
        ('0', 'Completely Disagree')
    ], validators=[DataRequired()])

    q7 = RadioField('Instructor encourage asking of questions and discussions in the classroom', choices=[
        ('4', 'Completely Agree'),
        ('3', 'Agree'),
        ('2', 'Neutral'),
        ('1', 'Disagree'),
        ('0', 'Completely Disagree')
    ], validators=[DataRequired()])

    q8 = RadioField('Instructor was accessible outside the classroom', choices=[
        ('4', 'Completely Agree'),
        ('3', 'Agree'),
        ('2', 'Neutral'),
        ('1', 'Disagree'),
        ('0', 'Completely Disagree')
    ], validators=[DataRequired()])

    q9 = RadioField('Instructor responded well to student doubts in class', choices=[
        ('4', 'Completely Agree'),
        ('3', 'Agree'),
        ('2', 'Neutral'),
        ('1', 'Disagree'),
        ('0', 'Completely Disagree')
    ], validators=[DataRequired()])

    q10 = RadioField('Explanations in classroom were clear and to the point', choices=[
        ('4', 'Completely Agree'),
        ('3', 'Agree'),
        ('2', 'Neutral'),
        ('1', 'Disagree'),
        ('0', 'Completely Disagree')
    ], validators=[DataRequired()])

    q11 = RadioField('Instructor was interested in and respectful to students', choices=[
        ('4', 'Completely Agree'),
        ('3', 'Agree'),
        ('2', 'Neutral'),
        ('1', 'Disagree'),
        ('0', 'Completely Disagree')
    ], validators=[DataRequired()])

    q12 = RadioField('Instructor was reasonably prompt in returning student papers', choices=[
        ('4', 'Completely Agree'),
        ('3', 'Agree'),
        ('2', 'Neutral'),
        ('1', 'Disagree'),
        ('0', 'Completely Disagree')
    ], validators=[DataRequired()])

    text_area = TextAreaField('Comments')

    submit = SubmitField('Submit')
