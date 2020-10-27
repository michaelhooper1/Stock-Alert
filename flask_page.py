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

    def __init__(self, name, username, email, password):
        self.name = name
        self.username = username
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

        email = request.form["email"]
        session["email"] = email

        username = request.form["username"]
        session["username"] = username

        preencrypted_password = request.form["password"]
        password = sha256_crypt.encrypt(preencrypted_password)
        session["password"] = password

        confirmed_password = request.form["confirm"]
        
        if confirmed_password != preencrypted_password:
            flash("The password fields do not match, please type again.")
            return redirect(url_for("register"))
        
        if not username:
            return "Missing Username", 400
        if not email:
            return "Missing email", 400
        if not password:
            return "Missing Password", 400

        new_user = User(name = name, username = username, email = email, password= password)
        db.session.add(new_user)
        db.session.commit()
        flash("Welcome, {}".format(new_user.username))
        return redirect(url_for("user"))
      
    return render_template("register.html")
    
   
   



@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        user = request.form["nm"]
        password = request.form["password"]
        session["user"] = user

        data = c.execute("SELECT * FROM users WHERE username = (%s)",
                             thwart(request.form['username']))

        found_user = sha256_crypt.verify(password, data)

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