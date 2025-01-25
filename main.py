
from flask import Flask, render_template, redirect, request, send_from_directory, url_for, session
import os, bcrypt
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Integer, String, select, LargeBinary, update
from sqlalchemy.orm import Mapped, mapped_column
import numpy as np

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

# Create the User model
class User(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[bytes] = mapped_column(LargeBinary)
    salt: Mapped[bytes] = mapped_column(LargeBinary, unique=True, nullable=False)


class Email_Key(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    register_key: Mapped[str] = mapped_column(String, unique=True)


class Timestamp(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    time_key: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)


class steel_weights_data(db.Model):
    __tablename__ = 'steel_weights'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    unit_weight: Mapped[int] = mapped_column(Integer, nullable=False)


with app.app_context():
    db.create_all()


## Base routes
@app.route("/")
def home():
    return redirect("/howto")


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return redirect('/')


@app.route("/howto")
def howto():
    return render_template("howto.html")


@app.route("/search")
def search():
    return render_template("search.html")


@app.route("/data/")
def data():
    if 'username' in session:
        return render_template("data_upload.html")
    else:
        return redirect('/adminlogin')


## Admin login to check if the admin is correct
@app.route("/adminlogin")
def login():
    return render_template("login.html")


@app.route("/user_val", methods=['POST'])
def user_val():
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
            session['username'] = uname
            return redirect('/data')


## Stuff to send register email and to add that to the data base 
@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/register_email')
def register_email():
    return render_template('register_email.html')


@app.route("/register_act", methods=['POST'])
def register_act():
    register_key = np.array2string(np.random.randint(9, size=12))
    email = request.form["sine"]
    link = "https://hrtdatabase.uk/register"
    email_reg = Email_Key(
        register_key=register_key
    )
    db.session.add(email_reg)
    db.session.commit()
    email_sending.send_pass_reg(email, link, register_key)
    return redirect('/')
## Route to create the user and too process that into the data base


@app.route("/user/<int:id>")
def user(id):
    user = db.get_or_404(User, id)
    return redirect('/')


@app.route('/create_user', methods=["POST"])
def create_user():
    a = db.session.execute(select(Email_Key).where(Email_Key.register_key == request.form["key"])).scalar()
    print(request.form["key"])
    print(a)
    if a is None:
        return redirect('/register')
    else:
        user = User(
            username=request.form["username"],
            password=bcrypt.hashpw(bytes(request.form["password"], 'utf-8'), salt),
            salt=salt
        )
        db.session.add(user)
        db.session.delete(a)
        db.session.commit()
        return redirect(url_for("user", id=user.id))


if __name__ == '__main__':
    ## contex = ('/home/sarah/sambashare/Steel Weight Calculator/cert/fullchain.pem', '/home/sarah/sambashare/Steel Weight Calculator/cert/privkey.pem') ## ToDO Change fullchain.pem
    app.run(host="192.168.0.15", port=5001, debug=True)


