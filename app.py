from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "hello"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = timedelta(minutes=5)

db = SQLAlchemy(app)

values = {}
values["calories"] = 0
values["fats"] = 0
values["sugars"] = 0
values["carbs"] = 0
loggedIn = False


class users(db.Model):
	_id = db.Column("id", db.Integer, primary_key=True)
	email = db.Column(db.String(100), nullable=False)
	password = db.Column(db.String(100), nullable=False)

	calories = db.Column(db.Integer)
	fats = db.Column(db.Integer)
	sugars = db.Column(db.Integer)
	carbs = db.Column(db.Integer)

	def __init__(self, email, password):
		self.email = email
		self.password = password
		self.calories = values["calories"]
		self.fats = values["fats"]
		self.sugars = values["sugars"]
		self.carbs = values["carbs"]


@app.route("/")
@app.route("/home")
def home():
	return render_template("index.html", logged=loggedIn, nutrients=values)

@app.route("/view")
def view():
	return render_template("view.html", data=users.query.all())

@app.route("/login", methods=["POST", "GET"])
def login():
	if request.method == "POST":
		loggedIn = True
		session.permanent = True

		userEmail = request.form["em"]
		userPass = request.form["pw"]
		
		session["userEmail"] = userEmail
		session["userPass"] = userPass

		found_user = users.query.filter_by(email=userEmail).first()

		if found_user:
			if found_user.password == userPass:
				flash("Login Successful!", "info")
				return redirect(url_for("home"))
			else:
				flash("Incorrect Password!", "error")
				return render_template("login.html")
		else:
			flash("This email does not correspond to an account!", "error")
			return render_template("login.html")

	else:
		if "user" in session:
			flash("Already Logged In!", "info")
			return redirect(url_for("home"))
		return render_template("login.html")

@app.route("/register", methods=["POST", "GET"])
def register():

	if request.method == "POST":
		loggedIn = True
		session.permanent = True
		
		userEmail = request.form["em"]
		userPass = request.form["pw"]
		
		session["userEmail"] = userEmail
		session["userPass"] = userPass

		found_user = users.query.filter_by(email=userEmail).first()
		
		if found_user != None:
			flash("This email is already in use!", "error")
			return render_template("register.html")
		else:
			usr = users(userEmail, userPass)
			db.session.add(usr)
			db.session.commit()

			flash("Registration Successful!", "info")
			return redirect(url_for("home"))
	else:
		if "userEmail" in session:
			flash("Already Logged In!", "info")
			return redirect(url_for("home"))
		else:
			flash("GET", "info")
			return render_template("register.html")

@app.route("/add")
def add():
	if loggedIn:
		return render_template("add.html")
	else:
		flash("Login to Add Food Values!")
		return redirect(url_for("login"))

@app.route("/logout")
def logout():
	if "userEmail" in session:
		userEmail = session["userEmail"]
		userPass = session["password"]

		session.pop("userEmail", None)
		session.pop("userPass", None)

		loggedIn = False
		flash("You have been logged out!", "info")
	else:
		flash("You are not logged in!", "error")
	
	return redirect(url_for("home"))

@app.route("/reset")
def reset():
	users.query.delete()
	db.session.commit()

	session.pop("userName", None)
	session.pop("userEmail", None)
	session.pop("userPass", None)

	loggedIn = False

	return redirect(url_for("home"))

if __name__ == "__main__":
	db.create_all()
	app.run(debug=True);