import os
from flask import (Flask, flash, render_template, redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/view_entries")
def view_entries():
    entries = mongo.db.entries.find()
    return render_template("entries.html", entries=entries)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        registration_code = request.form.get("reg-code")
        if registration_code == "T1":
            user_type = "teacher"
        elif registration_code == "P1":
            user_type = "parent"
        else:
            flash("Registration code not valid")
            return redirect(url_for("register"))

        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "user_type": user_type,
            "password": generate_password_hash(request.form.get("password"))
        }

        mongo.db.users.insert_one(register)
            #put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        #check if username exists in staff, parent, or student databases
        existing_staff = mongo.db.staff.find_one(
            {"username": request.form.get("username").lower()})
        existing_parent = mongo.db.parents.find_one(
            {"username": request.form.get("username").lower()})
        existing_student = mongo.db.students.find_one(
            {"username": request.form.get("username").lower()})
        
        if existing_staff:
            #ensure hashed password matches user input
            if check_password_hash(
                existing_staff["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(request.form.get("username")))
            else:
                #invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for('login'))

        elif existing_parent:
            #ensure hashed password matches user input
            if check_password_hash(
                existing_parent["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(request.form.get("username")))
            else:
                #invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for('login'))
        
        elif existing_student:
            #ensure hashed password matches user input
                if check_password_hash(
                    existing_student["password"], request.form.get("password")):
                    session["user"] = request.form.get("username").lower()
                    flash("Welcome, {}".format(request.form.get("username")))
                else:
                    #invalid password match
                    flash("Incorrect Username and/or Password")
                    return redirect(url_for('login'))
        
        else:
            #username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for('login'))

    return render_template("login.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
        port=int(os.environ.get("PORT")),
        debug=True)