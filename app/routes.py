
from flask import Flask, render_template,Blueprint

main = Blueprint('main', __name__, template_folder='templates')

@main.route('/home')
def home():
    return render_template('base.html')

