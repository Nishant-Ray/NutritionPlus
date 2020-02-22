import os
from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from flask_session import Session

app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

app.secret_key = "hello"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = timedelta(minutes=5)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQLAlchemy(app)

values = {}
values["calories"] = 0
values["fats"] = 0
values["carbs"] = 0
values["sugar"] = 0

loggedIn = False

factsCount = 1
ingredientsCount = 1

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(100), nullable=False)
	password = db.Column(db.String(100), nullable=False)


	def __repr__(self):
		return '<User %r>' % self.email


@app.route("/")
@app.route("/home")
def home():
	if "userEmail" in session:
		return render_template("index.html", logged=True, nutrients=values)
	else:
		return render_template("index.html", logged=False, nutrients=values)

@app.route("/view")
def view():
	return render_template("view.html", data=User.query.all())


@app.route("/login", methods=["POST", "GET"])
def login():
	if request.method == "POST":
		
		session.permanent = True

		userEmail = request.form["em"]
		userPass = request.form["pw"]

		session["userEmail"] = userEmail
		session["userPass"] = userPass

		found_user = User.query.filter_by(email=userEmail).first()

		if found_user:
			if found_user.password == userPass:
				#flash("Login Successful!", "info")
				return redirect(url_for("home"))
			else:
				#flash("Incorrect Password!", "error")
				return render_template("login.html")
		else:
			#flash("This email does not correspond to an account!", "error")
			return render_template("login.html")

	else:
		if "user" in session:
			#flash("Already Logged In!", "info")
			return redirect(url_for("home"))
		return render_template("login.html")

@app.route("/register", methods=["POST", "GET"])
def register():

	if request.method == "POST":
		session.permanent = True
		
		userEmail = request.form["em"]
		userPass = request.form["pw"]
		
		session["userEmail"] = userEmail
		session["userPass"] = userPass

		db.create_all()

		found_user = User.query.filter_by(email=userEmail).first()
		
		if found_user != None:
			#flash("This email is already in use!", "error")
			return render_template("register.html")
		else:
			usr = User(email=userEmail, password=userPass)
			db.session.add(usr)
			db.session.commit()
			loggedIn = True
			#flash("Registration Successful!", "info")
			return render_template("index.html", logged=True)
	else:
		if "userEmail" in session:
			#flash("Already Logged In!", "info")
			return redirect(url_for("home"))
		else:
			return render_template("register.html")

@app.route("/facts", methods=["POST", "GET"])
def facts():
	global factsCount
	
	if "userEmail" in session:
		if request.method == "GET":
			return render_template("upload_facts.html")
		else:
			target = os.path.join(APP_ROOT, "/Data/Family/Nishant/Flasks/AZHacks/factImages")
			print(target)

			if not os.path.isdir(target):
				os.mkdir(target)

			for file in request.files.getlist("file"):
				print(file)
				filename = "facts_data" + str(factsCount) + ".jpg"
				destination = "/".join([target, filename])
				print(destination)
				file.save(destination)
				factsCount += 1

			return redirect(url_for("facts_info"))
	else:
		return redirect(url_for("login"))

@app.route("/facts_info")
def facts_info():
	return render_template("facts_info.html")

@app.route("/ingredients", methods=["POST", "GET"])
def ingredients():
	global ingredientsCount
	
	if "userEmail" in session:
		if request.method == "GET":
			return render_template("upload_ingredients.html")
		else:
			target = os.path.join(APP_ROOT, "/Data/Family/Nishant/Flasks/AZHacks/ingredientsImages")
			print(target)

			if not os.path.isdir(target):
				os.mkdir(target)

			for file in request.files.getlist("file"):
				print(file)
				filename = "ingredients_data" + str(ingredientsCount) + ".jpg"
				destination = "/".join([target, filename])
				print(destination)
				file.save(destination)
				ingredientsCount += 1

			

			return redirect(url_for("ingredients_info"))
	else:
		return redirect(url_for("login"))

@app.route("/ingredients_info")
def ingredients_info():
	return render_template("ingredients_info.html")

@app.route("/logout")
def logout():
	if "userEmail" in session:
		userEmail = session["userEmail"]
		userPass = session["userPass"]

		session.pop("userEmail", None)
		session.pop("userPass", None)

		loggedIn = False
		#flash("You have been logged out!", "info")
	#else:
		#flash("You are not logged in!", "error")
	
	return redirect(url_for("home"))

@app.route("/reset")
def reset():
	User.query.delete()
	db.session.commit()

	session.pop("userName", None)
	session.pop("userEmail", None)
	session.pop("userPass", None)

	loggedIn = False

	factsCount = 1
	ingredientsCount = 1

	return redirect(url_for("home"))

if __name__ == "__main__":
	db.create_all()
	app.run(debug=True);