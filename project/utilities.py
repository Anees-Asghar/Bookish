import requests

from . import db
from .models import Book


# Get books with query string from api
def fetch_books(query_string):

	url = 'https://www.googleapis.com/books/v1/volumes?q=' + str(query_string)
	res = requests.get(url)

	if res.status_code != 200:
		return None

	return res.json()['items']


# Get book info by id form api
def fetch_info(book_id):

	url = "https://www.googleapis.com/books/v1/volumes/" + book_id
	res = requests.get(url)
	return res.json() if res.status_code == 200 else None


# Add book to database table if doesn't exist already
def add_book_to_table(book_info):

	book_id = book_info['id']

	# If book already exists return id
	book = Book.query.filter_by(book_id=book_id).first()
	if book:
		return
	
	# Create new book instance
	new_book = create_book_instance(book_info)

	# Add book to sessions
	db.session.add(new_book)


def remove_book_from_table(book_id):

	# Delete if book with id exists
	book = Book.query.filter_by(book_id=book_id).first()
	if book:
		db.session.delete(book)


def create_book_instance(book_info):

	new_book = Book(book_id = book_info['id'])

	try:
		new_book.title = book_info['volumeInfo']['title']
	except:
		new_book.title = 'No title'
	try:
		new_book.authors = ", ".join(book_info['volumeInfo']['authors'])
	except:
		new_book.authors = 'Unknown'
	try:
		new_book.published_date = str(book_info['volumeInfo']['publishedDate'])
	except:
		new_book.published_date = 'Unknown'
	try:
		new_book.description = book_info['volumeInfo']['description']
	except:
		new_book.description = 'No description provided.'
	try:
		new_book.categories = ", ".join(book_info['volumeInfo']['categories'])
	except:
		new_book.categories = 'Unknown'
	try:
		new_book.small_url = book_info['volumeInfo']['imageLinks']['thumbnail']
	except:
		new_book.small_url = '/images/no-cover.jpg'
	try:
		new_book.large_url = book_info['volumeInfo']['imageLinks']['small']
	except:
		new_book.large_url = new_book.small_url
	try:
		new_book.preview_link = book_info['volumeInfo']['previewLink']
	except:
		new_book.preview_link = '#'

	return new_book