import os
import datetime

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///database.db")




@app.route("/")
@login_required
def index():
    items = db.execute("SELECT * FROM list WHERE id = :id", id=session["user_id"])
    print(items)
    return render_template("index.html", items=items)




@app.route("/add", methods=["GET","POST"])
@login_required
def add():
    """ Add a list item """
    if request.method == "POST":
        item = request.form.get("item")
        add = db.execute("INSERT INTO list (id, item)  VALUES(:id, :item)", id=session["user_id"], item=item)
        return redirect("/")
    else:
        return render_template("/add.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("/error.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("/error.html")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return
        id = db.execute("SELECT id FROM users ORDER BY id DESC LIMIT 1")[0]['id']+1
        if not id:
            id = 1

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/delete", methods=["GET", "POST"])
@login_required
def delete():
    if request.method == "POST":
        item = request.form.get("item")
        delete = db.execute("DELETE FROM list WHERE id = :id AND item = :item VALUES(:id, :item)", id=session["user_id"], item=item)
        return redirect("/")
    else:
        items = db.execute("SELECT * FROM list WHERE id = :id", id=session["user_id"])
        return render_template("/delete.html", items=items)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""


    if request.method == "POST":
        # ensure username was submitted
        if not request.form.get("username"):
            return render_template("/error.html")

        # ensure password was submitted
        elif not request.form.get("password"):
            return render_template("/error.html")

        # ensure password and verified password is the same
        elif request.form.get("password") != request.form.get("confirmation"):
            return render_template("/error.html")
        try:
            new_id = db.execute("SELECT id FROM users ORDER BY id DESC LIMIT 1")[0]['id']+1 #Gets first row in reversed query then takes the list that is returned and gets the first element then the value in the key 'id' and pluses one.
        except IndexError:
            id = 1

        # insert the new user into users, storing the hash of the user's password
        result = db.execute("INSERT INTO users (id, username, hash)  VALUES(:id, :username, :hash)", id=id, username=request.form.get("username"), hash=generate_password_hash(request.form.get("password")))
        if not result:
            return render_template("/error.html")

        session["user_id"] = result
        return render_template("index.html")

    else:
        return render_template("register.html")

