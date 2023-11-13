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
debug = os.environ.get("DEBUG", False)
parent_code = os.environ.get("PARENT_CODE")
teacher_code = os.environ.get("TEACHER_CODE")

mongo = PyMongo(app)


@app.errorhandler(404)
def client_error(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("errors/500.html"), 500


@app.route("/<path:path>")
def path_error(path):
    return render_template("errors/404.html"), 404


@app.context_processor
def get_user_type():
    if "user" in session:
        user_type = mongo.db.users.find_one({"username": session["user"]})["user_type"]
    else:
        user_type = ""
    return dict(user_type=user_type)


@app.route("/view_reading_sessions")
def view_reading_sessions():
    reading_sessions = list(mongo.db.reading_sessions.find().sort("date", -1))
    users = list(mongo.db.users.find())
    students = list(mongo.db.students.find())
    return render_template("reading_sessions.html", reading_sessions=reading_sessions, users=users, students=students)


@app.route("/my_reading_sessions/<username>")
def my_reading_sessions(username):
    username = mongo.db.users.find_one({"username": session["user"]})
    if session["user"]:
        reading_sessions = list(mongo.db.reading_sessions.find().sort("date", -1))
        users = list(mongo.db.users.find())
        students = list(mongo.db.students.find())
        return render_template("my_reading_sessions.html", username=username, users=users, reading_sessions=reading_sessions, students=students)
    return redirect(url_for("login"))


@app.route("/students")
def students():
# get all students from the database
    students = list(mongo.db.students.find().sort("lname", 1))
    teachers = list(mongo.db.users.find({"user_type": "teacher"}))
    return render_template("students.html", teachers=teachers, students=students)


@app.route("/my_students/<username>")
def my_students(username):
    #get the session user's username from the database
    username = mongo.db.users.find_one(
        {"username": session["user"]})
    if session["user"]:
        students = list(mongo.db.students.find().sort("lname", 1))
        return render_template("my_students.html", username=username, students=students)
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        registration_code = request.form.get("reg-code")
        if registration_code == teacher_code:
            user_type = "teacher"
        elif registration_code == parent_code:
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
            "title": request.form.get("title").lower(),
            "fname": request.form.get("fname").lower(),
            "lname": request.form.get("lname").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }

        mongo.db.users.insert_one(register)
        #put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for("my_students", username=session["user"]))
        
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
                user = mongo.db.users.find_one({"username": request.form.get("username").lower()})
                flash("Welcome, {title} {lname}".format(title=user["title"].capitalize(), lname=user["lname"].capitalize()))
                return redirect(url_for("my_students", username=session["user"]))
            else:
                #invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for('login'))
        
        else:
            #username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for('login'))

    return render_template("login.html")


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
            "fname": request.form.get("fname").lower(),
            "lname": request.form.get("lname").lower(),
            "reading_level": request.form.get("reading_level"),
            "teacher": ObjectId(request.form.get("teacher")),
            "parent": parent
        }
        mongo.db.students.insert_one(student)
        flash("Student Successfully Added")
        return redirect(url_for("my_students", username=session["user"]))
        
    teachers = list(mongo.db.users.find({"user_type":"teacher"}).sort("surname", 1))
    return render_template("add_student.html", teachers=teachers)


@app.route("/edit_student/<student_id>", methods=["GET", "POST"])
def edit_student(student_id):
    # find the student
    student = mongo.db.students.find_one({"_id": ObjectId(student_id)})
    user_id = mongo.db.users.find_one({"username": session["user"]})["_id"]
    # the user must be a parent or teacher of the student to edit
    if student["parent"] == user_id or student["teacher"] == user_id:
        if request.method == "POST":
            submit = {
                "fname": request.form.get("fname").lower(),
                "lname": request.form.get("lname").lower(),
                "reading_level": request.form.get("reading_level"),
                "teacher": ObjectId(request.form.get("teacher")),
            }
            mongo.db.students.update_one({"_id": ObjectId(student_id)}, {"$set": submit})
            flash("Student Successfully Updated")
            return redirect(url_for("my_students", username=session["user"]))
        teachers = list(mongo.db.users.find({"user_type":"teacher"}).sort("surname", 1))
        return render_template("edit_student.html", student=student, teachers=teachers)
    flash("You don't have permission to edit this student")
    return redirect(url_for("my_students", username=session["user"]))


@app.route("/delete_student/<student_id>")
def delete_student(student_id):
    # find the student
    student = mongo.db.students.find_one({"_id": ObjectId(student_id)})
    user_id = mongo.db.users.find_one({"username": session["user"]})["_id"]
    # the user must be a parent or teacher of the student to delete
    if student["parent"] == user_id or student["teacher"] == user_id:
        mongo.db.students.delete_one({"_id": ObjectId(student_id)})
        mongo.db.reading_sessions.delete_many({"student": ObjectId(student_id)})
        flash("Student and All Associated Reading Sessions Successfully Deleted")
        return redirect(url_for("my_students", username=session["user"]))
    flash("You don't have permission to delete this student")
    return redirect(url_for("my_students", username=session["user"]))


@app.route("/delete_user/<username_id>")
def delete_user(username_id):
    user = mongo.db.users.find_one({"username": session["user"]})
    flash("User Account Deleted")
    session.pop("user")
    mongo.db.users.delete_one(user)
    return redirect(url_for("register"))


@app.route("/update_reading_levels/<username>", methods=["GET", "POST"])
def update_reading_levels(username):
    if request.method == "POST":
        # insert post method here!
        submit = {
            "reading_level": request.form.get("reading_level")
        }
    username = mongo.db.users.find_one(
        {"username": session["user"]})
    if session["user"]:
        students = list(mongo.db.students.find().sort("lname", 1))
        return render_template("update_reading_levels.html", username=username, students=students)
    return redirect(url_for("login"))


@app.route("/update_teacher/<user>", methods=["GET", "POST"])
def update_teacher(user):
    if request.method == "POST":
        # insert post method here!
        submit = {
            "teacher": request.form.get("teacher")
        }
    user = mongo.db.users.find_one(
        {"username": session["user"]})
    if session["user"]:
        students = list(mongo.db.students.find().sort("lname", 1))
        teachers = list(mongo.db.users.find({"user_type": "teacher"}).sort("lname"))
        return render_template("update_teacher.html", user=user, students=students, teachers=teachers)
    return redirect(url_for("login"))


@app.route("/log_reading_session", methods=["GET", "POST"])
def log_reading_session():
    if request.method == "POST":
        logged_by = mongo.db.users.find_one({"username": session["user"]})["_id"]
        reading_session = {
            "student": ObjectId(request.form.get("student")),
            "date": request.form.get("date"),
            "title": request.form.get("title").lower(),
            "book_level": request.form.get("book_level"),
            "comment": request.form.get("comment"),
            "logged_by": logged_by
        }
        mongo.db.reading_sessions.insert_one(reading_session)
        flash("Reading Session Successfully Added")
        return redirect(url_for("view_reading_sessions"))
    user = mongo.db.users.find_one({"username": session["user"]})
    students = list(mongo.db.students.find().sort("lname", 1))
    student_count = 0
    for student in students:
        if user["_id"] == student["parent"] or user["_id"] == student["teacher"]:
            student_count += 1
    if student_count == 0:
        flash("You have no students. Please remind parents to sign up.")
        return redirect(url_for('my_students', username=session['user']))
    return render_template("log_reading_session.html", students=students, user=user)


@app.route("/edit_reading_session/<reading_session_id>", methods=["GET", "POST"])
def edit_reading_session(reading_session_id):
    # find the reading session
    reading_session = mongo.db.reading_sessions.find_one({"_id": ObjectId(reading_session_id)})
    user_id = mongo.db.users.find_one({"username": session["user"]})["_id"]
    # the session["user"] must be the user who created the task
    if user_id == reading_session["logged_by"]:
        if request.method == "POST":
            reading_session = {
                "student": ObjectId(request.form.get("student")),
                "date": request.form.get("date"),
                "title": request.form.get("title").lower(),
                "book_level": request.form.get("book_level"),
                "comment": request.form.get("comment"),
            }
            mongo.db.reading_sessions.update_one({ "_id": ObjectId(reading_session_id) }, { "$set": reading_session })
            flash("Reading Session Successfully Updated")
            return redirect(url_for("view_reading_sessions"))
        students = list(mongo.db.students.find().sort("lname", 1))
        return render_template("edit_reading_session.html", reading_session=reading_session, students=students)
    flash("You don't have access to edit this reading session")
    return redirect(url_for('my_reading_sessions', username=session['user']))


@app.route("/delete_reading_session/<reading_session_id>")
def delete_reading_session(reading_session_id):
    # find the reading session
    reading_session = mongo.db.reading_sessions.find_one({"_id": ObjectId(reading_session_id)})
    user_id = mongo.db.users.find_one({"username": session["user"]})["_id"]
    # the session["user"] must be the user who created the task
    if user_id == reading_session["logged_by"]:
        mongo.db.reading_sessions.delete_one({"_id": ObjectId(reading_session_id)})
        flash("Reading Session Successfully Deleted")
        return redirect(url_for("my_reading_sessions"))
    flash("You don't have access to delete this reading session")
    return redirect(url_for('my_reading_sessions', username=session['user']))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
        port=int(os.environ.get("PORT")),
        debug = debug)