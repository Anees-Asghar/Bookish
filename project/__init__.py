import os
import secrets

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()

def create_app():

	project_dir = os.path.dirname(os.path.abspath(__file__))
	database_file = "sqlite:///{}".format(os.path.join(project_dir, "bookish_db.db"))

	app = Flask(__name__)
	app.config['SQLALCHEMY_DATABASE_URI'] = database_file

	secret = secrets.token_urlsafe(32)
	app.config['SECRET_KEY'] = secret

	db.init_app(app)

	login_manager = LoginManager()
	login_manager.login_view = 'auth.login'
	login_manager.init_app(app)

	from .models import User, User_Book

	@login_manager.user_loader
	def load_user(user_id):
		return User.query.get(int(user_id))

	from .main import main as main_blueprint
	app.register_blueprint(main_blueprint)

	from .auth import auth as auth_blueprint
	app.register_blueprint(auth_blueprint)

	return app