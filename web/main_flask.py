from app_flask import *
from flask import render_template
from flask import request, session, redirect, url_for
import requests
from models import User, Item


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
        return render_template("error.html")

@app.route('/item/<int:item_id>')
def item(item_id):
    try:
        data = session.get('items_data')
        selected_item = data[item_id]
        selected_item["item_index"] = item_id


        user_id = session.get('uid')
        
        return render_template("item.html", item=selected_item, user_id=user_id, item_id=item_id)
    except IndexError:
        return render_template("error.html", message="Item not found.")


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if session['authenticated'] != True:
        return render_template("error.html")
    

    if request.method == 'POST':
        item_title = request.form.get('item_title')
        item_description = request.form.get('item_description')
        item_cost = request.form.get('item_cost')
        item_image = request.form.get('item_image')
        item_owner = session['uid']

        # Подготовка данных в формате JSON
        data = {
            'item_title': item_title,
            'item_description': item_description,
            'item_cost': item_cost,
            'item_owner': item_owner,
            'item_image': item_image,
        }
        response = requests.post('http://localhost:8000/upload', json=data)

        if response.status_code == 200:
            return redirect(url_for('items'))
        else:
            return render_template('error.html', message='Failed to upload product')

    return render_template('upload.html')

@app.route("/cart_get")
def cart_get():
    if session.get('authenticated') != True:
        return render_template("error.html")
    
    user_id = session.get('uid')
    response = requests.get("http://localhost:8000/user/cart", params={'user_id': user_id})
    if response.status_code == 200:
        data = response.json()
        return render_template("cart.html", data=data)
    else:
        return render_template("error.html")
    
@app.route('/add_to_cart/<int:user_id>/<int:item_id>', methods=['POST', 'GET'])
def add_to_cart(user_id, item_id):
    if session['authenticated'] != True:
        return render_template("error.html")
    try:
        # Убедимся, что тело JSON соответствует модели ItemCreate
        payload = {
            "user_id": user_id,
            "item_id": item_id
        }

        response = requests.post("http://localhost:8000/add_to_cart", json=payload)
        if response.status_code == 200:
            return redirect(url_for('items'))
        else:
            return f"Something went wrong while adding item to cart: {response.text}"
    except Exception:
        return "something went wrong in flask"
    
# @app.route("/cart_confirm", methods=["POST"])
# def cart_confirm():
#     selected_items = request.form.getlist('selected_items[]')
#     if not selected_items:
#             return "No items to buy"
#     user_id = session.get('uid')
#     items_data = session.get("items_data", [])
#     items_to_buy = [{"item_id": int(item_id), "user_id": int(user_id)} for item_id in selected_items]
#     response = requests.post("http://localhost:8000/cart-confirm", json=items_to_buy)
#     if response.status_code != 200:
#         return render_template("error.html")
    
#     session['items_data'] = items_data
#     return render_template("confirm_buy")

@app.route("/cart_remove_multiple", methods=['POST'])
def cart_remove_multiple():
    try:
        # Получаем список выбранных предметов из формы
        selected_items = request.form.getlist('selected_items[]')
        print(selected_items)

        if not selected_items:
            return "No items selected for removal"

        # Получаем данные пользователя и корзины
        user_id = session.get('uid')
        items_data = session.get('items_data', [])

        # Преобразуем список в список словарей
        items_to_remove = [{"item_id": int(item_id), "user_id": int(user_id)} for item_id in selected_items]
        print(items_to_remove)
        # Отправляем запрос на удаление всех выбранных предметов
        response = requests.post("http://localhost:8000/remove-multiple-from-cart", json=items_to_remove)

        if response.status_code != 200:
            return f"Failed to remove item(s) from cart: {response.text}"

        # Обновляем данные сессии
        session['items_data'] = items_data

        # Возвращаем успешный результат или перенаправляем пользователя
        return redirect(url_for('cart_get'))
    except Exception as e:
        return f"Something went wrong: {str(e)}"


@app.route('/reviews')
def reviews():
    try:
        # Fetch reviews from the FastAPI endpoint
        response = requests.get("http://localhost:8000/get_reviews")

        if response.status_code == 200:
            reviews_data = response.json()
        else:
            reviews_data = []

        return render_template("reviews.html", reviews_data=reviews_data)

    except Exception as e:
        return f"Something went wrong: {str(e)}"

@app.route('/create_review', methods=['POST', 'GET'])
def create_review():
    try:
        # Получаем данные отзыва из формы
        user_id = session.get('uid')
        text = request.form.get('reviewText')
        rating = request.form.get('rating')

        # Подготавливаем данные для отправки на FastAPI
        data = {
            'user_id': user_id,
            'text': text,
            'rating': rating
        }

        # Отправляем запрос на FastAPI
        response = requests.post("http://localhost:8000/add_review", json=data)

        # Проверяем статус-код ответа
        if response.status_code == 200:
            return redirect( url_for('reviews') )
        else:
            return f"Failed to create review: {response.text}"

    except Exception as e:
        return f"Something went wrong: {str(e)}"
    

@app.route('/profile')
def profile():
    user_id = session.get('uid')
    try:
        # Fetch user data from the FastAPI endpoint
        response = requests.get(f"http://localhost:8000/get_user_data/{user_id}")

        if response.status_code == 200:
            user_data = response.json()
        else:
            user_data = {}

        return render_template("profile.html", user_data=user_data)

    except Exception as e:
        return f"Something went wrong: {str(e)}"
    


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        app.run(debug=True)