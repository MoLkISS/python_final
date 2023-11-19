from app_flask import *
from flask import render_template
from flask import request, session, redirect, url_for
import requests
from models import User, Item, Shop


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
        if response.status_code == 200:
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

@app.route('/items')
def items():
    response = requests.get('http://localhost:8000/items/')
    if response.status_code == 200:
        data = response.json()
        session['items_data'] = data
        return render_template("items.html", data=enumerate(data))
    else:
        return render_template("warning.html")

# Ваш Flask-маршрут
@app.route('/item/<int:item_index>')
def item(item_index):
    try:
        data = session.get('items_data', [])
        selected_item = data[item_index]
        selected_item["item_index"] = item_index
        print(selected_item)
        return render_template("item.html", item=selected_item)
    except IndexError:
        return render_template("error.html", message="Item not found.")

@app.route("/cart_get")
def cart_get():
    if session['authenticated'] != True:
        return render_template("warning.html")
    
    user_id = session.get('uid')
    response = requests.get("http://localhost:8000/user/cart", params={'user_id': user_id})
    if response.status_code == 200:
        data = response.json()
        return render_template("cart.html", data=data)
    else:
        return render_template("warning.html")
    
@app.route("/cart/<int:item_index>")
def cart(item_index):
    if session['authenticated'] != True:
        return render_template("warning.html")
    try:

        user_id = session['uid']
        user = db.session.query(User).filter_by(user_id=user_id).first()
        
        items_data = session.get('items_data', [])
        selected_item = items_data[item_index]
        selected_item["item_owner"] = user_id
        selected_item["item_description"] = ""
            
        # Убедимся, что тело JSON соответствует модели ItemCreate
        payload = {
            "item_title": selected_item["item_title"],
            "item_description": selected_item["item_description"],  # Добавьте описание, если оно доступно
            "item_cost": selected_item['item_cost'],
            "item_owner": session["uid"],
            "item_image": selected_item["item_image"]
        }
        print(payload)

        response = requests.post("http://localhost:8000/add-to-cart", json=payload)
        if response.status_code == 200:
            return redirect(url_for('items'))
        else:
            return f"Something went wrong while adding item to cart: {response.text}"
    except Exception:
        return "something went wrong in flask"


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        app.run(debug=True)