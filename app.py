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
        existing_staff = mongo.db.staff.find_one(
            {"username": request.form.get("username").lower()})
        existing_parent = mongo.db.parents.find_one(
            {"username": request.form.get("username").lower()})
        existing_student = mongo.db.students.find_one(
            {"username": request.form.get("username").lower()})

        if existing_staff or existing_parent or existing_student:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "fname": request.form.get("fname"),
            "lname": request.form.get("lname"),
            "password": generate_password_hash(request.form.get("password"))
        }

        registration_code = request.form.get("reg-code")
        if registration_code == "123":
            mongo.db.staff.insert_one(register)
            #put the new user into 'session' cookie
            session["user"] = request.form.get("username").lower()
            flash("Staff Registration Successful!")
        elif registration_code == "456":
            mongo.db.parents.insert_one(register)
            #put the new user into 'session' cookie
            session["user"] = request.form.get("username").lower()
            flash("Parent Registration Successful!")
        else:
            flash("Registration code not valid")
        

    return render_template("register.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
        port=int(os.environ.get("PORT")),
        debug=True)