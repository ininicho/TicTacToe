import os
import requests

from flask import Flask, session, redirect, render_template, request, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
database = scoped_session(sessionmaker(bind=engine))
db = database()

# Login required function
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# INDEX
@app.route("/", methods=["GET","POST"])
@login_required
def index():
    return render_template("index.html")

# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    
    # Make sure no one's logged in
    session.clear()

    # When user POST
    if request.method == "POST":

        # Checks username
        if not request.form.get("username"):
            return render_template("error.html", message="Must Provide Username")
        
        # Checks password
        elif not request.form.get("username"):
            return render_template("error.html", message="Must Provide Password")
        
        rows = db.execute("SELECT * FROM users WHERE username = :username", {"username":request.form.get("username")}).fetchall()

        # Check username and password validity
        if len(rows) != 1:
            return render_template("error.html", message="Invalid Username")
        elif not check_password_hash(rows[0]["password"], request.form.get("password")):
            return render_template("error.html", message="Wrong Password")
        
        # Remember session id
        session['user_id'] = rows[0]["id"]

        # Redirect to main page
        return redirect("/")
    
    # When user GET
    else:
        return render_template("login.html")
    
# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():

    # Make sure no one's logged in
    session.clear()

    # When user POST
    if request.method == "POST":

        rows = db.execute("SELECT * FROM users").fetchall()
        n = len(rows)

        # Check if username
        if not request.form.get("username"):
            return render_template("error.html", message="Must Provide Username")
        for i in range(n):
            if request.form.get("username") in rows[i]["username"]:
                return render_template("error.html", message="Username Taken")
        
        # Check Password and Confirmation
        if not request.form.get("password"):
            return render_template("error.html", message="Must Provide Password")
        elif not request.form.get("confirmation"):
            return render_template("error.html", message="Must Provide Password Confirmation")
        elif request.form.get("password") != request.form.get("confirmation"):
            return render_template("error.html", message="Password Confirmation Wrong")

        username = request.form.get("username")
        password = request.form.get("password")

        hash_password = generate_password_hash(password)

        # Adds data to users table
        db.execute("INSERT INTO users (id,username, password) VALUES (:id,:username,:password)", {"id":n+1, "username":username, "password":hash_password})

        # Changes session user_id
        user_id = db.execute("SELECT id FROM users WHERE username = :username", {"username": username}).fetchone()
        session['user_id'] = user_id["id"]

        db.commit()

        # Redirect to main page
        return redirect("/")

    # When user GET
    else:
        return render_template("register.html")

# LOGOUT
@app.route("/logout")
def logout():

    # Clear Session
    session.clear()

    # Redirect to login form
    return redirect("/")

# SEARCH
@app.route("/search", methods=["POST"])
@login_required
def search():
    # Gets Search Request
    search = request.form.get("search")
    search = "%" + search + "%"

    # Select books that suit search request
    rows = db.execute("SELECT isbn, title, author, year FROM books WHERE title LIKE :search OR isbn LIKE :search OR author LIKE :search ORDER BY title",
                        {"search": search}).fetchall()

    # Create list of books
    rows_list = []

    for row in rows:
        row_list = []
        for i in range(4):
            row_list.append(row[i])
        rows_list.append(row_list)

    # Returns Error if no book found
    if len(rows_list) == 0:
        return render_template("search.html", found=0)
    
    # Renders search.html with book lists
    else:
        return render_template("search.html", found=1, rows=rows_list, n=len(rows_list))

# BOOK
@app.route("/book/<isbn>", methods=["GET", "POST"])
@login_required
def book(isbn):
    # When User posts
    if request.method == "POST":

        # Check if review and rating provided
        if not request.form.get("review"):
            return render_template("error.html", message="Review required")
        elif not request.form.get("rating"):
            return render_template("error.html", message="Rating required")
        
        # Check if user already posted a review
        rows = db.execute("SELECT * FROM reviews WHERE id=:id AND isbn=:isbn", {"id":session['user_id'], "isbn":isbn}).fetchone()
        if rows is None:
            db.execute("INSERT INTO reviews (id,isbn,rating,review) VALUES (:id, :isbn, :rating, :review)",
                        {"id": session['user_id'], "isbn":isbn, "rating":int(request.form.get("rating")), "review":request.form.get("review")})
            
            db.commit()

            link = "/book/" + isbn
            return redirect(link)
        
        else:
            return render_template("error.html", message="Already given review")

    # When User gets
    else:

        # Query book in database based on isbn in url
        book = db.execute("SELECT isbn, title, author, year FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()

        # Returns error if no book found
        if book is None:
            return render_template("error.html", message="No Book Found")
        
        # Create Dictionary of book data
        book_data = {}

        book_data['isbn'] = book['isbn']
        book_data['title'] = book['title']
        book_data['author'] = book['author']
        book_data['year'] = book['year']

        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "8yaFXPRSHViyzjy4OfQag", "isbns": isbn})
        query = res.json()

        book_data['rating'] = query['books'][0]['average_rating']
        book_data['count'] = query['books'][0]['reviews_count']

        # Query reviews of books
        reviews = db.execute("SELECT id, rating, review FROM reviews WHERE isbn=:isbn", {"isbn": isbn}).fetchall()

        # If no reviews queried
        if reviews is None:
            return render_template("book.html", book=book_data, reviews="", check=False)
        
        else:
            # Create list of reviews
            reviews_list = []

            for review in reviews:
                reviews_list.append([review['id'], review['rating'], review['review']])
            
            # Query username based on id
            for review in reviews_list:
                q = db.execute("SELECT username FROM users WHERE id=:id", {"id": review[0]}).fetchone()
                review[0] = q['username']

            return render_template("book.html", book=book_data, reviews=reviews_list, check=True)