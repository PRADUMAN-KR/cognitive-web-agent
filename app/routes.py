
from flask import Flask, render_template,Blueprint,session,request,flash,redirect,url_for
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import string
import datetime
from .models import User,db


main = Blueprint('main', __name__, template_folder='templates')

def generate_api_key(length=32):
    """Generate a secure random API key."""
    characters = string.ascii_letters + string.digits
    api_key = ''.join(secrets.choice(characters) for _ in range(length))
    return api_key

@main.route('/home')
def home():
    return render_template('base.html')

@main.route('/register',methods = ['GET',"POST"])
def user_regis():
    if "username" in session:
        return render_template("dashboard.html")
    
    if request.method == 'POST':
        fname = request.form(['fname'])
        lname = request.form(['lname'])
        username = request.form(['username'])
        email = request.form(['email'])
        password = request.form(['password'])
        datetime_registered = datetime.now() 
        
        existing_user = User.query.filter(User.username == username | User.email == email)

        if existing_user:
            flash("username or email already exists",'danger')
            return render_template('register.html')
        
        hashed_password = generate_password_hash(password)
        new_user = User(fname = fname, lname = lname, email = email,username = username, password = hashed_password,datetime_registered = datetime_registered)

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('main.user_login'))
    
    return render_template('register.html')
    
@main.route('/login',methods= ['GET','POST'])
def user_login():
    if 'username' in session:
        return redirect(url_for('routes.dashboard'))


    if request.method == 'POST':
        username = request.form(['username'])
        password = request.form(['password'])

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['username'] = username
            flash('login successfull','success')
            return redirect(url_for('routes.home'))
        else:
            flash('invalid username or password','danger')
            return redirect(url_for('user_login'))
        
    return render_template('login.html')



@main.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('user_login'))
    return render_template('dashboard.html')
        
 



        

