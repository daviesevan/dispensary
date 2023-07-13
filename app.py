from datetime import datetime
from flask import Flask,render_template,url_for,redirect,request,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin,login_user,LoginManager,login_required,logout_user,current_user
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash
import os

DB_NAME = "database.db"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
app.config['SECRET_KEY'] = '9d1e302104a9b91c669a998d2df41d835109e86feebe2fd986d028c7b343'
db = SQLAlchemy(app)

# Set up the application context
app.app_context().push()

# Now you can use the database within the application context
db.create_all()

ms = ['Married','Single','Divorced']
bg = ['A+','A-','B+','B-','AB+','AB-','O+','O-']

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    user = User.query.get(int(id))
    return user


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.String(20),unique=True, nullable=False)
    email = db.Column(db.String(120),unique=True, nullable=False)
    user_profile = db.Column(db.String(20), nullable=False,default='default.png')
    password = db.Column(db.String(30),nullable=False)
    patient = db.relationship('Std_registration', backref='patient',lazy=True)
    role = db.Column(db.String(10))

    def __init__(self, school_id,email, password, role):
        self.school_id = school_id
        self.email = email
        self.password = password
        self.role = role

    def __repr__(self):
        return f'User("{self.school_id}","{self.email}","{self.user_profile}")'
    
class Std_registration(db.Model):
        id = db.Column(db.Integer,primary_key=True)
        name = db.Column(db.String(40),nullable=False)
        date_registered = db.Column(db.DateTime(),nullable=False, default=datetime.utcnow)
        marital_status = db.Column(db.String(120), nullable=False)
        address = db.Column(db.String(120), nullable=False)
        phonenumber = db.Column(db.String(13),unique=True, nullable=False)
        email = db.Column(db.String(120),unique=True, nullable=False)
        height = db.Column(db.Integer, default=0)
        weight = db.Column(db.Integer, default=0)
        blood_type = db.Column(db.String(10))
        patient_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
        user_role = 'patient'
        def __repr__(self):
            return f'User("{self.name}","{self.email}","{self.date_registered}")'


@app.route('/checkin',methods=['POST','GET'])
@login_required
def checkin():
    if current_user.role == 'patient':
        
        if request.method == 'POST':
            name = request.form.get('name')
            date_registered_str = request.form.get('date_registered')
            marital_status = request.form.get('marital_status')
            address = request.form.get('address')
            phonenumber = request.form.get('phonenumber')
            email = request.form.get('email')
            height = request.form.get('height')
            weight = request.form.get('weight')
            blood_type = request.form.get('blood_type')
            date_registered = datetime.strptime(date_registered_str, '%Y-%m-%dT%H:%M')
            
            if marital_status not in ms:
                flash('The Marital status is invalid!', category='error')
            elif blood_type not in bg:
                flash('The Blood group is invalid!', category='error')
            elif len(name) < 5:
                flash('The username is too short!', category='error')
            else:
                new_reg = Std_registration(name=name,date_registered=date_registered,
                                        marital_status=marital_status,
                                        address=address,phonenumber=phonenumber,
                                        email=email,height=height,
                                        weight=weight,blood_type=blood_type,patient_id = current_user.id)
                db.session.add(new_reg)
                db.session.commit()
        return render_template('index.html',user=current_user, ms=ms)

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == 'POST':
        school_id = request.form.get('school_id')
        password = request.form.get('password')
        user = User.query.filter_by(school_id=school_id).first()
        if user:
            if check_password_hash(user.password,password):                
                login_user(user,remember=True)
                if current_user.role == 'doctor':
                    flash(f'Welcome back {current_user.school_id}!', category='success')
                    return redirect(url_for('admin'))
                flash(f'Welcome back {current_user.school_id}', category='error')
                return redirect(url_for('home'))                                                 
            else:
                flash('Wrong username or password!', category='error')
        flash('The School id doesn\'t exist! Please try again', category='error')
    return render_template('login.html',user=current_user)
    
@app.route('/')
@login_required
def home():
    if current_user.role == 'patient':
        return render_template('home.html')
    return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        school_id = request.form.get('school_id')
        password = request.form.get('password')
        role = request.form.get('role')
        user = User.query.filter_by(email=email).first()
        s_id = User.query.filter_by(school_id=school_id).first()
        if user:
            flash('Account with this email already exists!', category='error')
        if s_id:
            flash('Account with this Username already exists!', category='error')
        if not school_id or not email or not password:
            flash('Sorry we couldn\'t sign you in!', category='error')
        new_user = User(email=email,
                            school_id=school_id,
                            password=generate_password_hash(password,method = 'sha256'),
                            role=role)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user,remember=True)
        return redirect(url_for('login'))
        
    return render_template("signup.html",user=current_user)

@app.route('/admin')
@login_required
def admin():
    if current_user.role == 'doctor':
        std=Std_registration.query.all()
        return render_template('staff.html',std=std,user=current_user)
    else:
        return redirect(url_for('login'))

# @app.route('/profile/<school_id>')
# @login_required
# def profile(school_id):
#     school_id == current_user.school_id
#     return render_template('profile.html',user=current_user, school_id=school_id)

@app.route('/account', methods=['GET','POST'])
@login_required
def account():
    if request.method == 'POST':
        school_id = request.form.get('school_id')
        email = request.form.get('email')
        if school_id == current_user.school_id:
            flash('School ID cannot be changed.',category="warning")
        elif email != current_user.email:
            check_mail =User.query.filter_by(email=current_user.email)
            for i in range (len(check_mail)):
                print ("Email Already Exists!")
                flash('Email Already Exists! Please use a different Email address.',category='warning')
                break;
            db.session.commit()
            flash('Account has been updated succesfully',category='success')
    elif request.method == 'GET':
        school_id = current_user.email
        email = current_user.email
    return render_template('account.html',user=current_user)

if __name__ == '__main__':
    app.run(debug=True)