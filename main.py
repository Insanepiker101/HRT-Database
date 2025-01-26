
from flask import Flask, render_template, redirect, request, send_from_directory, url_for, session
import os, bcrypt
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Integer, String, select, LargeBinary, update
from sqlalchemy.orm import Mapped, mapped_column
import numpy as np
import email_sending
import admin

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.secret_key = os.urandom(24)

# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"

# initialize the app with the extension
db.init_app(app)
salt = bcrypt.gensalt()

# Create the User model that tracks the id, username, password, and salt
class User(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[bytes] = mapped_column(LargeBinary)
    salt: Mapped[bytes] = mapped_column(LargeBinary, unique=True, nullable=False)


# Create the Timestamp Model that tracks a time key
class Timestamp(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    time_key: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)


## With the app as contex create the database with the above models
with app.app_context():
    db.create_all()


## Home route, aka the base route, redirects to /howto possible depracation?
@app.route("/")
def home():
    return render_template("home.html")


# This is the post method that handles logging out the user from the session and deletes the session token
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return redirect('/')


## TODO This needs a search bar and a way to request the database
# Adds a way to search the batchs and get the data from the database without a login
@app.route("/search")
def search():
    return render_template("search.html")


## TODO is this good for this project?
# Checks if the session token matches one already logged in, and then renders the template
@app.route("/data/")
def data():
    if 'user' in session:
        return render_template("data_upload.html")
    else:
        return redirect('/adminlogin')


## Admin login to check if the admin is correct
@app.route("/adminlogin")
def login():
    return render_template("login.html")


## This is a post method that checks if the user details entered in the admin login are matching too the details in the user models in the database
@app.route("/user_val", methods=['POST'])
def user_val():
    x = True
    if x is True:
        uname = request.form.get("username")
        usalt = db.session.execute(select(User.salt).where(User.username == uname)).scalar()
        if usalt is None:
            return redirect('/')
        else:
            upass = bcrypt.hashpw(bytes(request.form["password"], 'utf-8'), usalt)
            a = db.session.execute(select(User).where(User.username == uname, User.password == upass)).scalar()
            if a is None:
                return redirect('/')
            else:
                session['user'] = uname + str(upass)
                return redirect('/data')
    elif x is not True:
        print("Gen First User")
        u_salt=bcrypt.gensalt()
        user = User(
            username=request.form["username"],
            password=bcrypt.hashpw(bytes(request.form["password"], 'utf-8'), u_salt),
            salt=u_salt
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("user", id=user.id))

## This method displays all the admins and there level, can also be used to remove admins
@app.route("/admins")
def admin():
    return admin.renderAdminstemplete()

## Main function that handles the run fuction and the ssl context
if __name__ == '__main__':
    ## contex = ('/home/sarah/sambashare/Steel Weight Calculator/cert/fullchain.pem', '/home/sarah/sambashare/Steel Weight Calculator/cert/privkey.pem') ## ToDO Change fullchain.pem
    app.run(host="localhost", port=5001, debug=True)