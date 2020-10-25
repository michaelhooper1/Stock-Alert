from flask import Flask, redirect, url_for, render_template, request, session, flash
import bcrypt
import os
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(days = 5)

db = SQLAlchemy(app)

class User(db.Model):
    _id = db.Column("id", db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    username = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.Text, nullable = False)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password


@app.route("/register", methods=["POST", "GET"])
def register():
    if "user" in session:
        flash("You're currently already logged in")
        return redirect(url_for("user"))

    if request.method == "POST":
        session.permanent = True
        new_user = ["name", "email", "username", "password", "confirm password"]

        name = request.form["name"]
        session["name"] = name

        email = request.form["name"]
        session["email"] = email

        username = request.form["username"]
        session["username"] = username

        preencrypted_password = request.form["password"]
        password = sha256_crypt.encrypt(preencrypted_password)
        session["password"] = password

        
      
    return render_template("register.html")
    
    """
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    if not username:
        return "Missing Username", 400
    if not password:
        return "Missing Password", 400

    hashed = bcrypt.hashpw(password.encode("utf-0"), bcrypt.gensalt())

    user = User(name = username, email= email, password = hashed)

    db.session.add(user)
    db.session.commit()

    return "Welcome {}".format(user.username)"""


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        user = request.form["nm"]
        session["user"] = user

        found_user = User.query.filter_by(name=user).first()

        if found_user:
            session["email"] = found_user.email

        else:
            flash("No such user exist, register to continue")
            return redirect(url_for("register"))

        flash("Login successful")
        return redirect(url_for("user"))
    else:
        if "user" in session:
            flash("You're currently logged in")
            return redirect(url_for("user"))

        return render_template("login.html")

@app.route("/view")
def view():
    return render_template("view.html", values=User.query.all())

@app.route("/")
def home():
    if "user" in session:
        return redirect(url_for("user"))
    else:
        flash("Please log in to access your information")
        return redirect(url_for("login"))


@app.route("/admin/")
def admin():
    return redirect(url_for("user", name = "Admin"))

@app.route("/<name>/portfolio")
def porfolio(name):
    return f"Hello, {name}!"


@app.route("/user", methods=["POST", "GET"])
def user():
    email = None
    if "user" in session:
        user = session["user"]

        if request.method == "POST":
            email = request.form["email"]
            session["email"] = email
            found_user = User.query.filter_by(name=user).first()
            found_user.email = email
            db.session.commit()
            flash("Email was saved.")
        else:
            if "email" in session:
                email = session["email"]
        return render_template("user.html", user = user)
    else:
        flash("Please log in to access your information")
        return redirect(url_for("login"))

@app.route("/logout")
def logout():
    if "user" in session:
        user = session["user"]
        flash(f"You have been logged out, {user}", "info")

    session.pop("user", None)
    session.pop("email", None)

    return redirect(url_for("login"))

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)