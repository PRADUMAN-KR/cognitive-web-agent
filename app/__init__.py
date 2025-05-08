from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#comfig and db
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'supersecretkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../instance/bots.db'

    db.init_app(app)

    from .routes import auth_routes, bot_routes, chat_routes
    app.register_blueprint(auth_routes.auth_bp)         # for modular route groups
    app.register_blueprint(bot_routes.bot_bp)
    app.register_blueprint(chat_routes.chat_bp)

    return app
