from flask import Flask, redirect, url_for, render_template, request, session, flash
import os
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt
import sqlite3
from stock_price_update import look_at_price, all_stat_lookup


app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(days = 5)

db = SQLAlchemy(app)

user_tracking_company = db.Table("user_tracking_company",
             db.Column(("user_id"), db.ForeignKey("user.id")),
             db.Column(("company_id"), db.ForeignKey("company.id")),
             db.Column(("desired_price"), db.Float))

class User(db.Model):
    _id = db.Column("id", db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    username = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.Text, nullable = False)

    tracks = db.relationship("Company", backref = "tracked_by", lazy = "dynamic", secondary = user_tracking_company)

    def __init__(self, name, username, email, password):
        self.name = name
        self.username = username
        self.email = email
        self.password = password


class Company(db.Model):
    _id = _id = db.Column("id", db.Integer, primary_key = True)
    c_name = db.Column(db.String(200))
    c_index = db.Column(db.String(5))
    
    _tracked_by = db.relationship("User", secondary = user_tracking_company, backref = db.backref("user_tracking_company_backref", lazy="dynamic"))

    def __init__(self, c_name, c_index):
        self.c_name = c_name
        self.c_index = c_index






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
        password = sha256_crypt.hash(preencrypted_password)
        session["password"] = password

        confirmed_password = request.form["confirm"]
        
        if confirmed_password != preencrypted_password:
            flash("The password fields do not match, please type again.")
            return redirect(url_for("register"))
        
        if not username:
            flash("Please enter a username")
        if not email:
            flash("Please enter an email")
        if not password:
            flash("Please enter a password")

        new_user = User(name = name, username = username, email = email, password= password)
        db.session.add(new_user)
        db.session.commit()
       
        flash("Welcome, {}".format(new_user.username))
        return redirect(url_for("user"))
      
    return render_template("register.html")
    
   
   



@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        with sqlite3.connect("users.sqlite3") as connection:

            session.permanent = True
            user = request.form["nm"]
            password = request.form["password"]
            session["user"] = user

            c = connection.cursor()

            data = c.execute("SELECT * FROM user WHERE username = '{}'".format(user))

            data = c.fetchone()[4]

            id_data = c.execute("SELECT id from user where username = '{}'".format(user))

            id_data = c.fetchone()[0]

            session["id"] = id_data
       

            found_user = sha256_crypt.verify(password, data)

            

            if found_user:
                #session["email"] = found_user.email
                return redirect(url_for("user"))

            elif not found_user:
                flash("Incorrect password, please enter your correct password")
                
                session.pop("user", None)
                return redirect(url_for("home"))

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
        user = session["name"]
        return redirect(url_for("user"))
    else:
        flash("Please log in to access your information")
        return redirect(url_for("login"))


@app.route("/admin/")
def admin():
    return redirect(url_for("user", name = "Admin"))

@app.route("/portfolio")
def porfolio():
    
    if "user" in session:
       

   
        c = sqlite3.connect("users.sqlite3").cursor()
        id_call = session["id"]
        
        tracking_data = c.execute("SELECT company_id FROM user_tracking_company WHERE user_id = '{}'".format(id_call))
        
        company_list = [x for x in tracking_data]
        

        if len(company_list) == 0:
            flash("You are not tracking anything")

        #Recall sqlAlchemy get() query is by primary key
        user = User.query.get(id_call)
    else:
        return redirect(url_for("login"))

    return render_template("portfolio.html", companies = user.tracks.all())

@app.route("/user", methods=["POST", "GET"])
def user():
    
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

@app.route("/add_company", methods=["POST", "GET"])
def add_tracking():
    if request.method == "POST":
        symbol = request.form["symbol"]
        session["symbol"] = request.form["symbol"]

        market = request.form["market"]
        session["market"] = request.form["market"]

        price = request.form["price"]
        session["price"] = request.form["price"]

        if not symbol or not market or not price:
            return render_template("404.html")

        

        return redirect(url_for("confirmation", symb = symbol, mark = market, pri = price))



    return render_template("add_company.html")

@app.route("/confirm", methods=["POST", "GET"])
def confirmation():
    sym = session["symbol"]
    mar = session["market"]
    desired_price = session["price"]

    if request.method == "POST":
        new_track = user_tracking_company(user_id = session["id"], )
        

        


        
    

    return render_template("confirm.html",company = all_stat_lookup(sym, mar), des_price = desired_price)



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