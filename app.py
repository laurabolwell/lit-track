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
@app.route("/view_reading_sessions")
def view_reading_sessions():
    reading_sessions = list(mongo.db.reading_sessions.find())
    users = list(mongo.db.users.find())
    students = list(mongo.db.students.find())
    return render_template("reading_sessions.html", reading_sessions=reading_sessions, users=users, students=students)


@app.route("/students", methods=["GET", "POST"])
def students():
# get the session user's students from the database
    students = list(mongo.db.students.find())
    return render_template("students.html", students=students)


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
        return redirect(url_for("profile", username=session["user"]))
        
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        #check if username exists
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        
        if existing_user:
            #ensure hashed password matches user input
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(request.form.get("username")))
                return redirect(url_for("profile", username=session["user"]))
            else:
                #invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for('login'))
        
        else:
            #username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for('login'))

    return render_template("login.html")


@app.route("/profile/<username>")
def profile(username):
    #get the session user's username from the database
    username = mongo.db.users.find_one(
        {"username": session["user"]})
    if session["user"]:
        return render_template("profile.html", username=username)
    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    #remove user from session cookies
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/add_student", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        parent = mongo.db.users.find_one({"username": session["user"]})["_id"]
        student = {
            "fname": request.form.get("fname"),
            "lname": request.form.get("lname"),
            "reading_level": request.form.get("reading_level"),
            "teacher": request.form.get("teacher"),
            "parent": parent
        }
        mongo.db.students.insert_one(student)
        flash("Student Successfully Added")
        return redirect(url_for("students"))
        
    teachers = mongo.db.users.find({"user_type":"teacher"}).sort("surname", 1)
    return render_template("add_student.html", teachers=teachers)


@app.route("/edit_student/<student_id>", methods=["GET", "POST"])
def edit_student(student_id):
    if request.method == "POST":
        parent = mongo.db.users.find_one({"username": session["user"]})["_id"]
        submit = {
            "fname": request.form.get("fname"),
            "lname": request.form.get("lname"),
            "reading_level": request.form.get("reading_level"),
            "teacher": request.form.get("teacher"),
            "parent": parent
        }
        mongo.db.students.update_one({"_id": ObjectId(student_id)}, {"$set": submit})
        flash("Student Successfully Updated")
        return redirect(url_for("students"))
    student = mongo.db.students.find_one({"_id": ObjectId(student_id)})
    teachers = mongo.db.users.find({"user_type":"teacher"}).sort("surname", 1)
    return render_template("edit_student.html", student=student, teachers=teachers)


@app.route("/log_reading_session", methods=["GET", "POST"])
def log_reading_session():
    if request.method == "POST":
        logged_by = mongo.db.users.find_one({"username": session["user"]})["_id"]
        reading_session = {
            "student": request.form.get("student"),
            "date": request.form.get("date"),
            "title": request.form.get("title"),
            "book_level": request.form.get("book_level"),
            "comment": request.form.get("comment"),
            "logged_by": logged_by
        }
        mongo.db.reading_sessions.insert_one(reading_session)
        flash("Reading Session Successfully Added")
        return redirect(url_for("view_reading_sessions"))
    students = mongo.db.students.find().sort("lname", 1)
    return render_template("log_reading_session.html", students=students)


@app.route("/edit_reading_session/<reading_session_id>", methods=["GET", "POST"])
def edit_reading_session(reading_session_id):
    reading_session = mongo.db.reading_sessions.find_one({"_id": ObjectId(reading_session_id)})
    students = mongo.db.students.find().sort("lname", 1)
    return render_template("edit_reading_session.html", reading_session=reading_session, students=students)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
        port=int(os.environ.get("PORT")),
        debug=True)