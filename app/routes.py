
from flask import Flask, render_template,Blueprint,session,request,flash,redirect,url_for,jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import string
import datetime
from sqlalchemy import or_
from .models import User,db,WebBot
from .utilsf import ask_rag,create_qa_chain,load_vectors
from flask_cors import CORS





main = Blueprint('main', __name__, template_folder='templates')
CORS(main)

def generate_api_key(length=32):
    """Generate a secure random API key."""
    characters = string.ascii_letters + string.digits
    api_key = ''.join(secrets.choice(characters) for _ in range(length))
    return api_key

@main.route('/')
def home():
    return render_template('base.html')

@main.route('/register',methods = ['GET',"POST"])
def user_regis():
    if "username" in session:
        return render_template("dashboard.html")
    
    if request.method == 'POST':
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        datetime_registered = datetime.datetime.now()   
        
        existing_user = User.query.filter(
            or_(User.username == username , User.email == email)).first()

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
        return redirect(url_for('main.dashboard'))


    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter(
    or_(User.email == username, User.username == username)
).first()

        if user and check_password_hash(user.password, password):
            session['username'] = user.username
            flash('login successfull','success')
            return render_template('dashboard.html')
        else:
            flash('invalid username or password','danger')
            return redirect(url_for('main.user_login'))
        
    return render_template('login.html')



@main.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('main.user_login'))
    
    chat_bots = WebBot.query.filter(WebBot.username == session['username']).all()
    if not chat_bots:
        chat_bots = None

    return render_template('dashboard.html',data = chat_bots)
        
 
@main.route('/create-bot', methods=['POST'])
def create_bot():
    if 'username' not in session:
        return redirect(url_for('main.user_login'))
    
    if request.method == 'POST':
        bot_name = request.form.get('bot_name')
        website_url = request.form.get('website_url')
        datetime_created = datetime.datetime.now()

        existing_bot = WebBot.query.filter(WebBot.bot_name == bot_name).first()

        if existing_bot:
            flash("chabot with name already exits,choose another name",'warning')
            return render_template('dashbord.html')
        
        api_key = generate_api_key()
        new_bot = WebBot(bot_name = bot_name, website_url = website_url, api_key = api_key, datetime_created = datetime_created)
        db.session.add(new_bot)
        db.session.commit()
        flash("new bot created", "success")
        return redirect(url_for('main.dashboard'))
    
@main.route('/ask', methods=['GET', 'POST'])
def ask():
    if 'username' not in session:
        return redirect

    store_name = "ameotech"
    vector_store = load_vectors(store_name)
    qa_chain = create_qa_chain(vector_store)

    data = request.get_json()
    print(">>>>>>>>>>>>>>>>>>>>>>",data)
    question = data.get('question', "")  

    if not question:
        return jsonify({'error': 'no question provided'}), 400  
    

    try:
        answer = ask_rag(question, qa_chain)
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500






