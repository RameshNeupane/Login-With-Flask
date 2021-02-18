from flask import Flask, render_template, request, redirect, session, flash
import re
import datetime
import hashlib
# Flask WTF 
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, InputRequired, ValidationError

# Flask Database
import os 
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = "MAKING FLASK FORM"
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'logindata.sqlite')}"

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
  
  
# custom validation for fullname
def validate_fullname(form, field):
  name = field.data
  name_re = re.findall("[a-zA-Z ]", name)
  if(''.join(name_re) != name):
    raise ValidationError("Alphabets and whitespace only.")
  
def validate_password(form, field):
  pwd = field.data
  pwd_re = re.findall("[a-zA-Z0-9!@$_()&]", pwd)
  if(''.join(pwd_re) != pwd):
    raise ValidationError("Alphabets, digits, !, @, $, _, (, ), & only.")

# Login form class
class Login(FlaskForm):
  fullname = StringField("Name: ", validators = [InputRequired(message = "Required."), validate_fullname, 
              Length(min = 10, max = 30, message = "Name must contain at least %(min)d characters.")])
  birthdate = DateField("Birthdate: ")
  email = StringField("Email: ", validators = [InputRequired(), Email()])
  password = PasswordField("Password: ", validators = [InputRequired(message = "Required."), validate_password,
              Length(min = 8, max = 8, message = "Password must be %(min)d character long.")])
  confirmPassword = PasswordField("Confirm Password: ", validators = [InputRequired(),
                      EqualTo("password", message = "Password must match.")])
  submit = SubmitField("Submit")

    
# make input data clean
def clean_data(fname, dob, email, pwd):
  fname = fname.strip()
  fname = fname.split(' ')
  cap_fname = []
  for name in fname:
    cap_fname.append(name.capitalize())
  fname = ' '.join(cap_fname)

  dob = dob.split('-')
  y, m , d = int(dob[0]), int(dob[1]), int(dob[2])
  dob = [y, m , d]
  
  pwd = hashlib.sha512(pwd.encode()).hexdigest()
  
  return [fname, dob, email, pwd]
  

@app.route("/", methods = ["GET", "POST"])
def login():
  log = Login(request.form)
  if request.method == "POST" and log.validate():
    old_name = session.get('name')
    if old_name is not None and old_name != log.fullname.data:
      flash("Name has been changed.")
      # return redirect("/")
    session['name'] = log.fullname.data
    
    fname = log.fullname.data
    dob = str(log.birthdate.data)
    email = log.email.data
    pwd = log.password.data
    data = clean_data(fname, dob, email, pwd)
    # database operation
    logindb.create_all()
    usr = LoginUser(fullname = data[0], birthdate = datetime.date(data[1][0], data[1][1], data[1][2]),
                    email = data[2], password = data[3])
    logindb.session.add(usr)
    try:
      logindb.session.commit()
      flash("User created successfully.")  
      return redirect("/success")
    except:
      logindb.session.rollback()
      flash("Something went wrong")
      return redirect("/")
    
  return render_template("login.html", login = log, name = session.get('name'))

@app.route("/success", methods = ['GET', 'POST'])
def success():
  last_user_id= logindb.session.query(LoginUser.fullname).count()
  last_user = LoginUser.query.filter_by(id = last_user_id).first()
  print(last_user)
  return render_template("success.html", user = last_user)