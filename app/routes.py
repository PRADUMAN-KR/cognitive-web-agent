
from flask import Flask, render_template,Blueprint
import secrets
import string


main = Blueprint('main', __name__, template_folder='templates')

def generate_api_key(length=32):
    """Generate a secure random API key."""
    characters = string.ascii_letters + string.digits
    api_key = ''.join(secrets.choice(characters) for _ in range(length))
    return api_key

@main.route('/home')
def home():
    return render_template('base.html')

 
