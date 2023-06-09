from flask import Flask, render_template, request, url_for, redirect, session
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from datetime import date

app = Flask(__name__)
# client = MongoClient('localhost', 27017)
# client = MongoClient('localhost', 27017, username='username', password='password')

client = MongoClient("mongodb+srv://hade:Loutre@cluster0.dkflsnn.mongodb.net/?retryWrites=true&w=majority")
db = client.flask_db
records = db.register

app.secret_key = "H4de"

user_collection = db.user
todo = db.todo
search_date = ""
search_name = ""
logged = False

import pymongo
import bcrypt




@app.route('/', methods=('GET', 'POST'))
def index():
    global search_date
    global search_name

    if request.method == 'POST' and "content" in request.form.keys():
        # first of 3 possible form : création form
        content = request.form['content']
        degree = request.form['degree']
        date_ = request.form['date']
        days = get_remainig_day(str(date.today()), date_)
        todo.insert_one({'content': content, 'degree': degree, 'date': date_, 'days': days})
        return redirect(url_for('index'))

    if request.method == 'POST' and "search_Date" in request.form.keys():
        # second of the 3 possible form, this form get a date for the next page : search_date
        search_date = request.form['search_Date']
        return redirect(url_for('search'))

    if request.method == 'POST' and "search_Name" in request.form.keys():
        # last of the 3 possible form, this form get a sring for the next page : search_name
        search_name = request.form['search_Name']
        return redirect(url_for('name'))

    all_todos = todo.find()
    return render_template('index.html', todos=all_todos, logged=logged)


def get_remainig_day(date1, date2):
    date1_c = datetime.strptime(date1, "%Y-%m-%d")
    date2_c = datetime.strptime(date2, "%Y-%m-%d")
    return (date2_c - date1_c).days


@app.route('/calender/', methods=('GET', 'POST'))
def callender():
    """
        fonction used to get all the Todos ordered by the time remaining
    """
    todos = todo.find()
    all_todo = []
    for thing in todos:
        i = 0;
        while (i < len(all_todo) and all_todo[i]['date'] < thing['date']):
            i += 1
        all_todo.insert(i, thing)
    return render_template('calender.html', todos=all_todo)


@app.route('/search_date/', methods=('GET', 'POST'))
def search():
    """
        fonction used to get all the Todos for witch the date is the same as the date search_date
    """
    todos = todo.find()
    all_todo = []
    for thing in todos:
        if thing['date'] == search_date:
            all_todo.append(thing)
    x = datetime(int(search_date[0:4]), int(search_date[5:7]), int(search_date[8:10]))
    return render_template('serach_date.html', todos=all_todo, day=x.day, month=x.strftime("%B"), year=x.year)


@app.route('/search_name/', methods=('GET', 'POST'))
def name():
    """
        fonction used to get all the Todos for witch the contnet start by the string search_name
    """
    todos = todo.find()
    all_todo = []
    for thing in todos:
        if len(search_name) <= len(thing['content']) and thing['content'][0:len(search_name)] == search_name:
            all_todo.append(thing)
    return render_template('serach_name.html', todos=all_todo, name=search_name)


@app.post('/<id>/delete/')
def delete(id):
    todo.delete_one({"_id": ObjectId(id)})
    return redirect(url_for('index'))


@app.route("/login", methods=["POST", "GET"])
def login():
    print("login")
    global logged
    message = 'Please login to your account'
    if "email" in session:
        logged = True
        return redirect(url_for("index"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        email_found = records.find_one({"email": email})
        if email_found:
            email_val = email_found['email']
            passwordcheck = email_found['password']

            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                session["email"] = email_val
                logged = True
                return redirect(url_for('index'))
            else:
                if "email" in session:
                    logged = True
                    return redirect(url_for("index"))
                message = 'Wrong password'
                return render_template('login.html', message=message)
        else:
            message = 'Email not found'
            return render_template('login.html', message=message)
    return render_template('login.html', message=message)

@app.route("/register", methods=["POST", "GET"])
def register():
    print("register")
    global logged
    if request.method == 'POST':
        user = request.form['password']
        password = request.form['password']
        email = request.form['email']

        user_found = records.find_one({"name": user})
        email_found = records.find_one({"email": email})

        if user_found:
            message = 'There already is a user by that name'
            return render_template('register.html', message=message)
        if email_found:
            message = 'This email already exists in database'
            return render_template('register.html', message=message)
        else:
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            user_input = {'name': user, 'email': email, 'password': hashed}
            records.insert_one(user_input)
            logged = True;
            return render_template('login.html',message="successfully register")
    return render_template('register.html')

@app.route("/logout", methods=["POST", "GET"])
def logout():
    global logged
    logged=False
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()
