import os
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from helpers import apology, login_required, lookup, usd


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


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""
    username = request.args.get("username")
    if len(username) < 1:
        print("false len")
        return jsonify("false")
    name = db.execute(f"SELECT * FROM users WHERE username = '{username}'")
    if name:
        print("false")
        return "false"
    else:
        print("true")
        return "true"

@app.route("/")
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/home")

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


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        if not request.form.get("username"):
            return apology("You must provied your UserName", 400)
        if not request.form.get("name"):
            return apology("You must provied your name", 400)
        if not request.form.get("password"):
            return apology("You must provied your password", 400)
        if not request.form.get("confirmation"):
            return apology("You must provied your password", 400)
        if (request.form.get("password") != request.form.get("confirmation")):
            return apology("password not the same", 400)
        if not request.form.get("email"):
            return apology("You must provied your email", 400)
        if not request.form.get("phone"):
            return apology("You must provied your phone", 400)
        if not request.form.get("country"):
            return apology("You must provied your country", 400)
        if not request.form.get("BloodType"):
            return apology("You must provied your BloodType", 400)
        hash = generate_password_hash(request.form.get("password"))
        user_name = db.execute("SELECT username FROM users WHERE username = :username",
                               username=request.form.get("username"))
        if user_name:
            return apology("taken", 400)
        db.execute("INSERT INTO users(username,hash,email,name,phone,country,type) VALUES(:username, :hash, :email, :name, :phone, :country, :type)", username=request.form.get("username"), hash=hash,
                    email=request.form.get("email"), name=request.form.get("name"), phone=request.form.get("phone"), country=request.form.get("country"), type=request.form.get("BloodType"))
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))
        session["user_id"] = rows[0]["id"]
        return redirect("/home")
    else:
        return render_template("register.html")

@app.route("/home", methods=["GET", "POST"])
def home():
    user = db.execute(f"SELECT * FROM users WHERE id = {session['user_id']}")
    return render_template("home.html", user=user)
@app.route("/donate", methods=["GET", "POST"])
def donate():
    if request.method == "POST":
        user = db.execute(f"SELECT * FROM users WHERE id = {session['user_id']}")
        db.execute("INSERT INTO donor(name,email,phone,country,type) VALUES(:name, :email, :phone, :country, :type)",
                    name=user[0]["name"], email=user[0]["email"], phone=user[0]["phone"], country=user[0]["country"], type=user[0]["type"])
        return redirect("/home")
    else:
        return render_template("donate.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)
# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
