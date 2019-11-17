from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from usfpes import app,db,login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    student_id = db.Column(db.String(8),nullable=False,unique=True)
    filled_survey = db.Column(db.Boolean(),unique=False, default=False)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"
'''
class Responses(db.Model):
    course_name = db.Column(db.String, nullable=False)

    course_id = db.Column(db.String, nullable=False)

    faculty_name = db.Column(db.String, nullable=False)

    dept = db.Column(db.String, nullable=False)

    q1 = db.Column(db.Integer, nullable=False)

    q2 = db.Column(db.Integer, nullable=False)

    q3 = db.Column(db.Integer, nullable=False)

    q4 = db.Column(db.Integer, nullable=False)

    q5 = db.Column(db.Integer, nullable=False)

    q6 = db.Column(db.Integer, nullable=False)

    q7 = db.Column(db.Integer, nullable=False)

    q8 = db.Column(db.Integer, nullable=False)

    q9 = db.Column(db.Integer, nullable=False)

    q10 = db.Column(db.Integer, nullable=False)

    q11 = db.Column(db.Integer, nullable=False)

    q12 = db.Column(db.Integer, nullable=False)

    comments = db.Column(db.String)


    def __repr__(self):
        return f"Feedback: ('{self.course_name}', '{self.course_id}', '{self.faculty_name}', '{self.dept}')"
'''
