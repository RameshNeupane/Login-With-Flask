from flask import Flask, render_template, request, redirect, session, flash
# Flask WTF 
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, InputRequired

# Flask Database
import os 
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = "MAKING FLASK FORM"
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'logindata.sqlite')}"
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False

logindb = SQLAlchemy(app)

# Model class definition for logindb
class LoginUser(logindb.Model):
  id = logindb.Column(logindb.Integer, primary_key = True)
  fullname = logindb.Column(logindb.String(30), unique = True)
  birthdate = logindb.Column(logindb.Date, nullable = True)
  email = logindb.Column(logindb.String, unique = True, nullable = False)
  password = logindb.Column(logindb.String)
  
  def __repr__(self):
    return '<LoginUser %r>' %self.fullname

# Login form class
class Login(FlaskForm):
  fullname = StringField("Name: ", validators = [InputRequired(message = "Required."), 
              Length(min = 10, max = 30, message = "Name must contain at least %(min)d characters.")])
  birthdate = DateField("Birthdate: ")
  email = StringField("Email: ", validators = [DataRequired(), Email()])
  password = PasswordField("Password: ", validators = [DataRequired(message = "Required."),
              Length(min = 8, max = 8, message = "Password must be %(min)d character long.")])
  confirmPassword = PasswordField("Confirm Password: ", validators = [DataRequired(),
                      EqualTo("password", message = "Password must match.")])
  submit = SubmitField("Submit")

@app.route("/", methods = ["GET", "POST"])
def login():
  log = Login(request.form)
  if request.method == "POST" and log.validate():
    old_name = session.get('name')
    if old_name is not None and old_name != log.fullname.data:
      flash("Name has been changed.")
    session['name'] = log.fullname.data
    return redirect("/success")
  return render_template("login.html", login = log, name = session.get('name'))

@app.route("/success", methods = ['GET', 'POST'])
def success():
  return render_template("success.html", name = session.get('name'))