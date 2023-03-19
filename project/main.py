import os
from . import db
from sqlalchemy import desc
from sqlalchemy.sql import func
from flask import Blueprint, redirect, request, render_template, url_for, send_from_directory, flash
from flask_login import login_required, current_user
from .models import status, User, User_Book, Book
from .utilities import fetch_books, fetch_info, add_book_to_table, remove_book_from_table, create_book_instance


main = Blueprint("main", __name__)


@main.route("/")
@login_required
def index():

    user_id = current_user.user_id

    # Querying all the books related to the user from the database
    reading_nows = db.session.query(User_Book, Book).filter(User_Book.user_id == user_id, User_Book.status == status.reading_now).filter(
        User_Book.book_id == Book.book_id).order_by(desc(User_Book.last_modified)).all()
    have_reads = db.session.query(User_Book, Book).filter(User_Book.user_id == user_id, User_Book.status == status.have_read).filter(
        User_Book.book_id == Book.book_id).order_by(desc(User_Book.last_modified)).all()
    to_reads = db.session.query(User_Book, Book).filter(User_Book.user_id == user_id, User_Book.status == status.to_read).filter(
        User_Book.book_id == Book.book_id).order_by(desc(User_Book.last_modified)).all()

    # Render template with all the relevant books
    return render_template('main/index.html',
                           have_reads=have_reads,
                           reading_nows=reading_nows,
                           to_reads=to_reads)


@main.route("/search", methods=["GET"])
def search():

    query_string = request.args.get('query_string')

    # Store list of book details
    books = []
    if query_string:
        raw_books = fetch_books(query_string)

        if raw_books:
            for b in raw_books:
                book = create_book_instance(b)
                books.append(book)

    # Render the tempalte with relevant books
    return render_template('main/search.html', query_string=query_string, books=books)


@main.route("/detail/<book_id>")
@login_required
def detail(book_id):

    # Get book details
    book_info = fetch_info(book_id)

    # Return and flash if book not found
    if not book_info:
        flash("Could not find book details.")
        return redirect(url_for('main.index'))

    # Make an instance of Book class using book data
    book = create_book_instance(book_info)

    # Check if existing book-user realtion exist and store relation in rel
    query = User_Book.query.filter_by(
        book_id=book_id, user_id=current_user.user_id,).first()
    rel = None
    if query:
        rel = query.status.name

    # store logged-in user review, if rel is 'have-read'
    user_review = None
    if rel == 'have_read':
        user_review = query

    # Query database for all reviews for book except logged-in user's
    reviews = db.session.query(User_Book, User).filter(User_Book.book_id == book_id, User_Book.user_id != current_user.user_id).filter(
        User_Book.user_id == User.user_id).order_by(desc(User_Book.last_modified)).all()

    # Query database for average rating for the book
    avg_rating = User_Book.query.with_entities(func.avg(User_Book.rating).label(
        'rating')).filter(User_Book.book_id == book_id).first()

    # Render template with relevant info
    return render_template('main/detail.html',
                           book=book,
                           user_relation=rel,
                           avg_rating=avg_rating,
                           user_review=user_review,
                           reviews=reviews)


# static images at url '/images/filename'
@main.route('/images/<filename>')
def serve_image(filename):
    project_dir = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(os.path.join(project_dir, 'static', 'images'), filename)


@main.route("/add-relation", methods=['POST'])
@login_required
def add_relation():

    user_id = current_user.user_id
    relation = request.form.get('relation')
    book_id = request.form.get('book_id')
    next_url = request.form.get('next_url')

    # Get book details from api
    book_info = fetch_info(book_id)

    # flash message if book not found
    if not book_info:
        flash('Could not find book.')
        if next_url:
            return redirect(next_url)
        return redirect(url_for('main.index'))

    # Add book to Books table if not already
    add_book_to_table(book_info)

    # Update existing user-book relation if any
    rel = User_Book.query.filter_by(user_id=user_id, book_id=book_id).first()
    new_relation = False

    if not rel:
        rel = User_Book(user_id=user_id, book_id=book_id)
        new_relation = True

    if relation == 'have_read':
        rel.status = status.have_read
        rating = request.form.get('rating')

        if not rating:
            flash('Please Rate the book.')
            if next_url:
                return redirect(next_url)
            return redirect(url_for('main.index'))

        rel.rating = rating
        rel.review = request.form.get('review')

    elif relation == 'reading_now':
        rel.status = status.reading_now

    elif relation == 'to_read':
        rel.status = status.to_read

    else:
        flash('Failed to update record. Try again.')
        if next_url:
            return redirect(next_url)
        return redirect(url_for('main.index'), book_id=book_id)

    # Add rel and book to database
    if new_relation:
        db.session.add(rel)
    db.session.commit()

    # Redirect to next_url if provided, default main.index
    if relation == 'have_read':
        flash('Review posted. Thank you!')

    if next_url:
        return redirect(next_url)

    return redirect(url_for('main.index', book_id=book_id))


@main.route("/remove-relations", methods=['POST'])
@login_required
def remove_all_relations():

    user_id = current_user.user_id
    book_id = request.form.get('book_id')
    next_url = request.form.get('next_url')

    # Delete if book-user relation exists
    rel = User_Book.query.filter_by(user_id=user_id, book_id=book_id).first()
    if rel:
        db.session.delete(rel)

        # Delete book from books if no further user-book relation with the book
        query = User_Book.query.filter_by(book_id=book_id).all()
        if not query:
            remove_book_from_table(book_id)

        db.session.commit()

    # Redirect to next_url if provided, default main.detail
    if next_url:
        return redirect(next_url)

    return redirect(url_for('main.index', book_id=book_id))
