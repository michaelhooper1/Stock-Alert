from flask import Flask, redirect, url_for, render_template, request, session, flash
import os
from datetime import timedelta

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.permanent_session_lifetime = timedelta(days = 5)


@app.route("/home/<name>/")
def home(name):
    return render_template("index.html", content = name)


@app.route("/admin/")
def admin():
    return redirect(url_for("user", name = "Admin"))

@app.route("/<name>/portfolio")
def porfolio(name):
    return f"Hello, {name}!"

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        user = request.form["nm"]
        session["user"] = user
        return redirect(url_for("user"))
    else:
        if "user" in session:
            return redirect(url_for("user"))
        return render_template("login.html")

@app.route("/user")
def user():
    if "user" in session:
        user = session["user"]
        return f"<h1>{user}</h1>"
    else:
        return redirect(url_for("login.html"))

@app.route("/logout")
def logout():
    if "user" in session:
        user = session["user"]
        flash(f"You have been logged out, {user}", "info")
    session.pop("user", None)

    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run()