from app_flask import *
from flask import render_template
from flask import request, session, redirect, url_for
from werkzeug.utils import secure_filename
import requests


from database.models import User, Work
from database.crud import add_user, add_work


@app.route('/home')
@app.route("/")
def home():
    is_authenticated = session.get('authenticated', False)
    return render_template("index.html", is_authenticated=is_authenticated)

@app.route("/register", methods=["GET", "POST"])
def register(context=None):
    if session.get('authenticated'):
        return redirect(url_for('home'))
    
    if request.method == "POST":
        data = {
            'login': request.form['login'],
            'email': request.form['email'],
            'password': request.form['password']
        }
        response = requests.post('http://localhost:8000/users/create/', json=data)
        if response:
            return redirect(url_for('login'))
        else:
            return f'User creation failed: {response.text}'
    return render_template("register.html", context=context)
    

@app.route("/login", methods=["GET", "POST"])
def login(context=None):
    if session.get('authenticated'):
        return redirect(url_for('home'))
    
    if request.method == "POST":
        user = db.session.query(User).filter_by(login=request.form['login'], password=request.form['password']).first()
        if user:
            session['authenticated'] = True
            session['uid'] = user.user_id
            session['login'] = user.login
            return redirect(url_for("home"))
        else:
            return render_template("login.html", context="try again, something went wrong")
    return render_template("login.html", context=context)

@app.route("/logout")
def logout():
    session.pop('authenticated', None)
    session.pop('uid', None)
    session.pop('login', None)
    return redirect(url_for('home'))