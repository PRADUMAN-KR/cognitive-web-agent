from flask import Blueprint, request, jsonify, render_template
from ..models import db, Bot
from ..utils.scraper import scrape_content
from ..utils.vectorizer import create_embeddings

bot_bp = Blueprint('bot', __name__)

@bot_bp.route('/create_bot', methods=['POST'])


def create_bot(): # accepts POST requests to create a new bot
    bot_name = request.form.get('bot_name')
    url = request.form.get('url')

    if not bot_name or not url:
        return jsonify({'error': 'Bot name and URL required'}), 400

    content = scrape_content(url)                               # scrape content from the URL
    
    """ if not content:
        return jsonify({'error': 'Failed to scrape content from the URL'}), 400
    if Bot.query.filter_by(name=bot_name).first():
        return jsonify({'error': 'Bot with this name already exists'}), 400
    if Bot.query.filter_by(url=url).first():
        return jsonify({'error': 'Bot with this URL already exists'}), 400 """ 
   
    vector_path = create_embeddings(content, bot_name)            # Converts content to vector embeddings using Hugging Face
    """if not vector_path:
        return jsonify({'error': 'Failed to create vector embeddings'}), 500
    # Check if bot with the same name or URL already exists
    existing_bot = Bot.query.filter((Bot.name == bot_name) | (Bot.url == url)).first()
    if existing_bot:
        return jsonify({'error': 'Bot with this name or URL already exists'}), 400
    # Check if the URL is already taken
    if Bot.query.filter_by(url=url).first():
        return jsonify({'error': 'Bot with this URL already exists'}), 400"""
    


    new_bot = Bot(name=bot_name, url=url, vector_path=vector_path) #Saves those embeddings into a FAISS vector index file
    db.session.add(new_bot)                    #Stores bot info in SQLite
    db.session.commit()

    return jsonify({'message': 'Bot created successfully', 'bot_name': bot_name})








from flask import session, redirect, url_for, render_template
from ..models import Bot


@bot_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    bots = Bot.query.all()
    return render_template('dashboard.html', bots=bots)



@bot_bp.route('/delete_bot/<int:bot_id>', methods=['POST'])
def delete_bot(bot_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    bot = Bot.query.get_or_404(bot_id)
    db.session.delete(bot)
    db.session.commit()

    return jsonify({'message': 'Bot deleted successfully'})