from flask import Flask, Blueprint, redirect, request, url_for, render_template, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user

from . import db
from .models import User


auth = Blueprint("auth", __name__)


@auth.route("/signup")
def signup():
	email = request.args.get('email')
	username = request.args.get('username')
	return render_template('auth/signup.html', email=email, username=username)


@auth.route("/signup", methods=['POST'])
def signup_post():

	email = request.form.get('email')
	username = request.form.get('username')
	password = request.form.get('password')

	if len(password) < 5:
		flash("Password must be atleast 5 characters.")
		return(redirect(url_for('auth.signup', email=email, username=username)))

	user = User.query.filter_by(email = email).first()

	if user:
		flash("User with this email already exists.")
		return redirect(url_for('auth.signup'))

	new_user = User(email = email, username = username, 
		password = generate_password_hash(password, method='sha256'))
	db.session.add(new_user)
	db.session.commit()

	flash("Account created successfully. Sign in now!")

	return redirect(url_for('auth.login'))


@auth.route("/login")
def login():
	url = request.args.get('next')
	email = request.args.get('email')
	return render_template('auth/login.html', email=email, next=url)


@auth.route("/login", methods=['POST'])
def login_post():
	
	url = request.args.get('next')

	email = request.form.get('email') # Check if email valid
	password = request.form.get('password')
	remember = True if request.form.get('remember') else False

	user = User.query.filter_by(email = email).first()

	if not user:
		flash("The user with the given email does not exist.")
		return redirect(url_for('auth.login'))

	if not check_password_hash(user.password, password):
		flash("The username and password don't match, try again.")
		return redirect(url_for('auth.login', email=email))

	login_user(user, remember=remember)

	flash("Signed in as {}.".format(user.username))
	
	if url:
		return redirect(url)
	else:
		return redirect(url_for('main.index'))


@auth.route("/logout")
def logout():
	logout_user()
	flash("Logged out successfully.")
	return redirect(url_for('auth.login'))