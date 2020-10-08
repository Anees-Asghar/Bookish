import enum
from flask_login import UserMixin
from sqlalchemy.sql import func

from . import db


class status(enum.Enum):
	reading_now = 'reading_now'
	to_read = 'to_read'
	have_read = 'have_read'


class User(UserMixin, db.Model):
	user_id = db.Column(db.Integer, primary_key=True, nullable=False)
	email = db.Column(db.String(50), unique=True, nullable=False)
	username = db.Column(db.String(50))
	password = db.Column(db.String(50))

	def get_id(self):
		return self.user_id

class Book(db.Model):
	book_id = db.Column(db.String(20), primary_key=True, nullable=False)
	title = db.Column(db.String(500), nullable=False)
	authors = db.Column(db.String(1000), nullable=False)
	published_date = db.Column(db.String(10), nullable=False)
	description = db.Column(db.String(2000), nullable=False)
	categories = db.Column(db.String(1000), nullable=False)
	small_url = db.Column(db.String(1000), nullable=False)
	large_url = db.Column(db.String(1000), nullable=False)
	preview_link = db.Column(db.String(1000), nullable=False)


class User_Book(db.Model):
	user_id = db.Column(db.Integer, db.ForeignKey(User.user_id), primary_key=True, nullable=False)
	book_id = db.Column(db.String(20), db.ForeignKey(Book.book_id), primary_key=True, nullable=False)
	status = db.Column(db.Enum(status), nullable=False)
	rating = db.Column(db.Float, db.CheckConstraint("rating >= 0 AND rating <= 5"), nullable=True)
	review = db.Column(db.String(1000), nullable=True)
	last_modified = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
