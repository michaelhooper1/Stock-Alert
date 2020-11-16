from flask import Flask, redirect, url_for, render_template, request, session, flash
import os
from sqlalchemy.orm import sessionmaker
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt
import sqlite3
from stock_price_update import look_at_price, all_stat_lookup, price_search


app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(days = 5)

db = SQLAlchemy(app)

class UserTrackingCompany(db.Model):
    __tablename__ = "UserTrackingCompany"
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key = True)
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"), primary_key = True)
    des_price = db.Column(db.Float)

    user = db.relationship("User", back_populates = "tracks")
    company = db.relationship("Company", back_populates = "tracked_by")


class User(db.Model):
    _id = db.Column("id", db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    username = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.Text, nullable = False)

    tracks = db.relationship("UserTrackingCompany", lazy="subquery", back_populates = "user")

    def __init__(self, name, username, email, password):
        self.name = name
        self.username = username
        self.email = email
        self.password = password


class Company(db.Model):
    _id = db.Column("id", db.Integer, primary_key = True)
    c_name = db.Column(db.String(200))
    c_index = db.Column(db.String(10))

    tracked_by = db.relationship("UserTrackingCompany", lazy="dynamic", back_populates = "company")

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

            session["user_data"] = data
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
def portfolio():
    
    if "user" in session:
       

   
        c = sqlite3.connect("users.sqlite3").cursor()
        id_call = session["id"]
        
        tracking_data = c.execute("SELECT company_id FROM UserTrackingCompany WHERE user_id = '{}'".format(id_call))
        tracking_data = c.fetchall()
        for i in range(len(tracking_data)):
            tracking_data[i] = int(''.join(str(ele) for ele in tracking_data[i])) 
        

        desired_price_data = c.execute("SELECT des_price FROM UserTrackingCompany WHERE user_id = '{}'".format(id_call))
        desired_price_data = c.fetchall()
        
        for i in range(len(desired_price_data)):
            desired_price_data[i] = float(''.join(str(ele) for ele in desired_price_data[i])) 
        

        
        company_list = []
        company_price_list = []

        for entry in tracking_data:
            company_data = c.execute("SELECT * FROM Company WHERE id = '{}'".format(entry))
            company_data = c.fetchone()
            company_list.append(company_data)
        

        for company in company_list:
            actual_price = price_search(company[1], company[2])
            company_price_list.append(actual_price)
        

        
        if len(company_list) == 0:
            flash("You are not tracking anything")

        #Recall sqlAlchemy get() query is by primary key
        user = User.query.get(id_call)
    else:
        return redirect(url_for("login"))

    return render_template("portfolio.html", companies = company_list, prices_list = company_price_list)

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
    if "user" in session:
        if request.method == "POST":
            symbol = request.form["symbol"]
            session["symbol"] = request.form["symbol"]

            market = request.form["market"]
            session["market"] = request.form["market"]

            price = request.form["price"]
            session["price"] = request.form["price"]

            if not symbol or not market or not price:
                return render_template("404.html")

            c = sqlite3.connect("users.sqlite3").cursor()
            try:
                company_check = c.execute("SELECT * FROM Company WHERE c_name = '{}' AND c_index = {}".format(symbol, market))
                company_check = c.fetchone()[0]

            except sqlite3.OperationalError:
                company_check = False

            if company_check:
                return redirect(url_for("confirmation", symb = symbol, mark = market, pri = price))

            else:
                new_company = Company(c_name = symbol, c_index = market)

                db.session.add(new_company)
                db.session.commit()
                return redirect(url_for("confirmation", symb = symbol, mark = market, pri = price))



        return render_template("add_company.html")

@app.route("/confirm", methods=["POST", "GET"])
def confirmation():
    sym = session["symbol"]
    mar = session["market"]
    desired_price = session["price"]


    with sqlite3.connect("users.sqlite3") as connection:
        c = connection.cursor()
        c_id = c.execute("SELECT id FROM Company WHERE c_name = '{}' AND c_index = '{}'".format(sym, mar))
        c_id = c.fetchone()[0]
        

    if request.method == "POST":

        
        
        
        track = UserTrackingCompany(des_price = desired_price)
        
        
        track.user_id = session["id"]
        track.company_id = c_id



        db.session.add(track)
        db.session.commit()
        flash("You've successfully added {} ({})".format(sym, mar))
        return redirect(url_for("portfolio"))

        


        
    

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