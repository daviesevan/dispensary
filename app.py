from datetime import datetime
from flask import Flask,render_template,url_for,redirect,request,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin,login_user,LoginManager,login_required,logout_user,current_user
from sqlalchemy.sql import func
from flask_mail import Mail
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
from itsdangerous.serializer import Serializer
import secrets

load_dotenv()
DB_NAME = "database.db"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
# Access the environment variables
mail_username = os.getenv('MAIL_USERNAME')
mail_password = os.getenv('MAIL_PASSWORD')
secret_key = os.getenv('SECRET_KEY')

app.config['SECRET_KEY'] = secret_key

# Initialize Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = mail_username
app.config['MAIL_PASSWORD'] = mail_password
app.config['MAIL_MAX_EMAILS '] = None
app.config['MAIL_SUPPRESS_SEND '] = app.testing

db = SQLAlchemy(app)
mail = Mail(app)
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
    user = User.query.get(int(id) if id is not None else None)
    return user


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False)
    school_id = db.Column(db.String(20),unique=True, nullable=False)
    email = db.Column(db.String(120),unique=True, nullable=False)
    user_profile = db.Column(db.String(20), nullable=False,default='default.png')
    password = db.Column(db.String(30),nullable=False)
    patient = db.relationship('Std_registration', backref='patient',lazy=True)
    role = db.Column(db.String(10))

    def __init__(self, school_id,username,email, password, role):
        self.school_id = school_id
        self.username = username
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
        

# Initialize the URL serializer for password reset tokens using secrets
secret = secrets.token_urlsafe(30)
print(secret)
serializer = Serializer(secret)


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
                try:
                    db.session.add(new_reg)
                    db.session.commit()
                    flash('Appointment booked successfully',category='success')
                    return redirect(url_for('home'))
                except:
                    flash('Looks like you have a pending appointment',category='error')
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
                    flash(f'Welcome back {current_user.username}!', category='success')
                    return redirect(url_for('admin'))
                flash(f'Welcome back {current_user.username}!', category='success')
                return redirect(url_for('home'))                                                 
            else:
                flash('Wrong username or password!', category='error')
        flash('The School id doesn\'t exist! Please try again', category='error')
    return render_template('login.html',user=current_user)
    
@app.route('/')
@login_required
def home():
    if current_user.role == 'patient':
        user = User.query.get(current_user.id)
        appointments = user.patient
        return render_template('home.html', appointments=appointments)
    return redirect(url_for('login'))


@app.route('/delete/<int:id>')
def delete(id):
    appointment_to_delete = Std_registration.query.get_or_404(id)
    try:
        db.session.delete(appointment_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        flash('There was a problem deleting a task',category='error')
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
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
                        username=username,
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
        std=Std_registration.query.order_by(Std_registration.date_registered).all()
        return render_template('staff.html',std=std,user=current_user)
    else:
        logout_user()
        return redirect(url_for('login'))

@app.route('/takeup/<int:id>')
@login_required
def takeup(id):
    if current_user.role == 'doctor':
        takeup = Std_registration.query.get_or_404(id)
        try:
            db.session.delete(takeup)
            db.session.commit()
            return redirect(url_for('admin'))
        except:
            flash('There was a problem deleting a task',category='error')
    return render_template('takeup.html') 


@app.route('/account', methods=['GET','POST'])
@login_required
def account():
    if request.method == 'POST':
        school_id = request.form.get('school_id')
        email = request.form.get('email')

        if school_id == current_user.school_id:
            flash('School ID cannot be changed.', category='error')
        elif email != current_user.email:
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash('If the email doesn\'t exist then It has been updated successfully.', category='warning')
            else:
                current_user.email = email
                current_user.school_id = school_id
                db.session.commit()
                flash('Account has been updated successfully.', category='success')
    return render_template('account.html', user=current_user)
    

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/forgot_password', methods=['GET', 'POST'])
@login_required
def forgot_password():
    if request.method == 'POST':
        user = User.query.filter_by(email=current_user.email).first()
        if user:
            # Generate the password reset token
            token = serializer.dumps(user.email, salt='reset-password')
            
            # Create the password reset URL
            reset_url = url_for('reset_password', token=token, _external=True)
            
            # Send the password reset email
            mail.send_message(
                subject='Reset Your Password',
                sender='noreply@dispensary.spu.ac.ke',
                recipients=[user.email],
                body=f"Please click the link below to reset your password:\n{reset_url}"
            )
            
            flash('If the Email exists in our database then Password reset instructions has been sent successfully.', category='success')
            return redirect(url_for('login'))
        else:
            flash('Email address not found.')
    return render_template('request-pass-change.html')



@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = serializer.loads(token, salt='reset-password', max_age=3600)
    except:
        flash('Invalid or expired token. Please request a new password reset.',category='error')
        return redirect(url_for('forgot_password'))
    
    user = User.query.filter_by(email=email).first()
    if not user:
        flash('Email address not found.')
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        # Change the user's password
        user.password = generate_password_hash(password)
        db.session.commit()
        
        # Send confirmation email
        mail.send_message(
            subject='Password Reset Successful',
            sender='noreply@dispensary.spu.ac.ke',
            recipients=[user.email],
            body='Your password has been successfully reset.'
        )
        
        # Flash a success message and redirect to the login page
        flash('Your password has been reset successfully.', category='success')
        return redirect(url_for('login'))
    
    return render_template('request-pass-change.html')

if __name__ == '__main__':
    app.run(debug=True)