from flask import Flask, render_template, url_for, request, redirect, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = '123456'  # Для использования сессий

# Путь к базе данных
DATABASE = 'base_1.db'

# Функция для получения цен на билеты
def get_ticket_prices():
    query = "SELECT adult_price, child_price FROM ticket_prices WHERE id = 1"
    return execute_query(query, fetchone=True)

def execute_query(query, params=(), fetchone=False, fetchall=False):
    try:
        with sqlite3.connect(DATABASE, timeout=10) as conn:
            cursor = conn.cursor()
            print(f"Executing query: {query} with params: {params}")  # Логируем запрос
            cursor.execute(query, params)
            if fetchone:
                return cursor.fetchone()  # Вернет одну строку
            if fetchall:
                return cursor.fetchall()  # Вернет все строки
            conn.commit()  # Важно для записи в базу
            print("Query executed successfully.")
    except sqlite3.Error as e:
        print(f"Ошибка работы с базой данных: {e}")
        return None

# Создание таблицы пользователей
def create_users_table():
    query = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        surname TEXT NOT NULL,
        phone TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
    """
    execute_query(query)

# Функция для создания таблицы с ценами билетов
def create_ticket_prices_table():
    query = """
    CREATE TABLE IF NOT EXISTS ticket_prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        adult_price INTEGER NOT NULL,
        child_price INTEGER NOT NULL
    )
    """
    execute_query(query)

def get_ticket_prices():
    query = "SELECT adult_price, child_price FROM ticket_prices WHERE id = 1"
    result = execute_query(query, fetchone=True)
    print(f"Результат get_ticket_prices: {result}")  # Логируем результат
    return result

# insert_ticket_prices(1000, 500)

def create_bookings_table():
    query = """
            CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            adults_count INTEGER NOT NULL,
            children_count INTEGER NOT NULL,
            total_price REAL NOT NULL,
            visit_date TEXT NOT NULL,
            park_name TEXT NOT NULL,
            booking_date TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """
    execute_query(query)

def create_booking(user_id, adults, children, total_price, visit_date, park_name):
    query = """
    INSERT INTO bookings (user_id, adults_count, children_count, total_price, visit_date, park_name)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    try:
        print(f"Параметры записи: user_id={user_id}, adults={adults}, children={children}, total_price={total_price}, visit_date={visit_date}, park_name={park_name}")
        execute_query(query, (user_id, adults, children, total_price, visit_date, park_name))
        print("Бронирование успешно добавлено.")
    except sqlite3.Error as e:
        print(f"Ошибка при записи бронирования: {e}")


# Фиктивные данные для рекомендованных и популярных мест
recommended_places = [
    {'image_url': 'static/image/park_1.jpg', 'name': 'Астра', 'description': 'Веселье и экстрим на захватывающих аттракционах для всей семьи..'},
    {"image_url": "static/image/park_2.jpg", "name": "Звездный Оазис", "description": "Идеальное место для ночных прогулок под звездами."},
    {"image_url": "static/image/park_3.jpg", "name": "Волшебный Мир", "description": "Сказочная атмосфера и развлечения для всей семьи."},
    {"image_url": "static/image/park_4.webp", "name": "Легенда Леса", "description": "Тайные тропы и захватывающие виды природы."},
    {"image_url": "static/image/park_5.jpg", "name": "Солнечный лес", "description": "Светлые рощи и спокойствие в каждом уголке."}
]


popular_places = [
    {"image_url": "static/image/popular_1.jpg", "name": "Набережная Счастья", "description": "Идеальное место для прогулок у воды с потрясающими видами."},
    {"image_url": "static/image/popular_2.webp", "name": "Центральный Сад", "description": "Тихий уголок природы в самом сердце города."},
    {"image_url": "static/image/popular_3.jpg", "name": "Сквер Искусств", "description": "Оазис вдохновения с живыми скульптурами и выставками."},
    {"image_url": "static/image/popular_4.jpg", "name": "Башня Ветра", "description": "Захватывающее место с видом на город и историю ветров."},
    {"image_url": "static/image/popular_5.jpg", "name": "Театр Под Звездами", "description": "Открытая сцена с невероятными вечерними представлениями."}
]

@app.route("/")
@app.route("/index")
def index():
    # Проверяем, авторизован ли пользователь
    logged_in = 'user' in session
    return render_template('index.html', logged_in=logged_in, 
                           recommended_places=recommended_places, 
                           popular_places=popular_places)
    

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        surname = request.form.get('surname')
        phone = request.form.get('phone')
        email = request.form.get('email')
        password = request.form.get('password')

        hashed_password = generate_password_hash(password)

        query = """
            INSERT INTO users (name, surname, phone, email, password) 
            VALUES (?, ?, ?, ?, ?)
        """
        try:
            with sqlite3.connect(DATABASE) as conn:
                cursor = conn.cursor()
                cursor.execute(query, (name, surname, phone, email, hashed_password))
                user_id = cursor.lastrowid  # Получаем ID нового пользователя

                session['user'] = {
                    'id': user_id,  # Сохраняем ID в сессии
                    'name': name,
                    'surname': surname,
                    'phone': phone,
                    'email': email
                }
                flash("Регистрация прошла успешно!", "success")
                return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            flash("Пользователь с таким номером телефона уже существует!", "error")
        except Exception as e:
            print(f"Ошибка при добавлении пользователя: {e}")
            flash("Произошла ошибка при регистрации. Попробуйте снова.", "error")

    return render_template('register.html')


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('password')

        # Проверяем данные пользователя в базе данных
        user = execute_query(
            "SELECT * FROM users WHERE name = ?", (name,), fetchone=True
        )

        if user and check_password_hash(user[5], password):  # user[5] - это хэш пароля
           session['user'] = {
                'id': user[0],  # user[0] - это id пользователя
                'name': user[1],
                'surname': user[2],
                'phone': user[3],
                'email': user[4]
            }
           flash("Вы успешно вошли!", "success")
           return redirect(url_for('index'))
        else:
            flash("Неверный логин или пароль!", "error")

    return render_template('vhod.html')

def get_user_bookings(user_id):
    query = """
    SELECT park_name, adults_count, children_count, total_price, visit_date, booking_date
    FROM bookings
    WHERE user_id = ?
    ORDER BY booking_date DESC
    """
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (user_id,))
            rows = cursor.fetchall()
            # Преобразуем данные в список словарей
            return [
                {
                    "park_name": row[0],
                    "adults_count": row[1],
                    "children_count": row[2],
                    "total_price": row[3],
                    "visit_date": row[4],
                    "booking_date": row[5]
                }
                for row in rows
            ]
    except Exception as e:
        print(f"Ошибка извлечения бронирований: {e}")
        return []

@app.route("/kab")
def kab():
    user = session.get('user')  # Получаем данные пользователя из сессии
    if not user:
        flash("Сначала войдите в систему.", "error")
        return redirect(url_for('login'))  # Перенаправляем на страницу входа
    
    # Получаем все бронирования пользователя
    bookings = get_user_bookings(user['id'])

    # Передаем пользователя и его бронирования в шаблон
    return render_template("kabinet.html", user=user, bookings=bookings)



@app.route("/bron", methods=["GET", "POST"])
def bron():
    # Проверка авторизации
    logged_in = 'user' in session
    if not logged_in:
        flash("Пожалуйста, войдите в систему, чтобы забронировать билеты.", "error")
        return redirect(url_for('login'))

    # Получаем цены на билеты
    ticket_prices = get_ticket_prices()
    if not ticket_prices:
        flash("Ошибка загрузки цен на билеты.", "error")
        return redirect(url_for('index'))

    adult_price, child_price = ticket_prices

    # Получаем название парка
    park_name = request.args.get("park_name")
    if not park_name:
        flash("Ошибка! Не выбран парк.", "error")
        return redirect(url_for('index'))

    
    if request.method == "POST":
        # Получение данных из формы
        visit_date = request.form.get("visit-date")
        adults = request.form.get("adults", 0)
        children = request.form.get("children", 0)
        try:
            adults = int(adults)
            children = int(children)
        except ValueError:
            flash("Некорректное количество взрослых или детей.", "error")
            return redirect(url_for("bron", park_name=park_name))
        # Проверка заполненности полей
        if not visit_date:
            flash("Пожалуйста, укажите дату посещения.", "error")
            return redirect(url_for("bron", park_name=park_name))
        # Рассчитываем стоимость
        total_price = (adults * adult_price) + (children * child_price)
        # Получаем ID пользователя
        user_id = session['user']['id']
        # SQL-запрос для записи
        query = """
            INSERT INTO bookings (user_id, adults_count, children_count, total_price, visit_date, park_name) 
            VALUES (?, ?, ?, ?, ?, ?)
        """
        try:
            with sqlite3.connect(DATABASE) as conn:
                cursor = conn.cursor()
                cursor.execute(query, (user_id, adults, children, total_price, visit_date, park_name))
                booking_id = cursor.lastrowid  # ID новой записи
                # Flash-сообщение об успешном бронировании
                flash(f"Ваше бронирование успешно создано! ID бронирования: {booking_id}", "success")
                return redirect(url_for('index'))
        except sqlite3.Error as e:
            print(f"Ошибка при записи бронирования: {e}")
            flash("Произошла ошибка при бронировании. Попробуйте снова.", "error")
    
        

    return render_template("park.html", park_name=park_name, logged_in=logged_in)


@app.route("/delete_booking", methods=["POST"])
def delete_booking():
    if 'user' not in session:
        flash("Для удаления бронирования нужно войти в систему.", "error")
        return redirect(url_for('login'))

    park_name = request.form.get("park_name")  # Получаем имя парка
    visit_date = request.form.get("visit_date")  # Получаем дату посещения

    if not park_name or not visit_date:
        flash("Ошибка! Не удалось найти нужное бронирование.", "error")
        return redirect(url_for('kab'))  # Перенаправляем на страницу личного кабинета

    query = "DELETE FROM bookings WHERE park_name = ? AND visit_date = ? AND user_id = ?"
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (park_name, visit_date, session['user']['id']))  # Удаляем только бронирования текущего пользователя
            conn.commit()

        flash("Бронирование успешно удалено.", "success")
    except sqlite3.Error as e:
        print(f"Ошибка при удалении бронирования: {e}")
        flash("Произошла ошибка при удалении бронирования. Попробуйте снова.", "error")

    return redirect(url_for('kab'))  # Перенаправляем на страницу с личным кабинетом


def calculate_total_price(adults_count, children_count):
    price_per_adult = 1000  # Стоимость для взрослого
    price_per_child = 500  # Стоимость для ребенка
    total_price = (adults_count * price_per_adult) + (children_count * price_per_child)
    return total_price

def update_booking(booking_id, visit_date, adults_count, children_count, total_price):
    query = """UPDATE bookings 
               SET visit_date = ?, adults_count = ?, children_count = ?, total_price = ? 
               WHERE id = ?"""
    
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (visit_date, adults_count, children_count, total_price, booking_id))
            conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка при обновлении бронирования: {e}")

def get_booking_by_park_and_date(park_name, visit_date):
    query = "SELECT * FROM bookings WHERE park_name = ? AND visit_date = ?"
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (park_name, visit_date))
        result = cursor.fetchone()
    return result

def get_booking_by_park_and_date(park_name, visit_date):
    query = "SELECT * FROM bookings WHERE park_name = ? AND visit_date = ?"
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (park_name, visit_date))
            booking = cursor.fetchone()
            if booking:
                # Преобразуем результат в словарь для удобства работы
                return {
                    'id': booking[0],
                    'user_id': booking[1],
                    'adults_count': booking[2],
                    'children_count': booking[3],
                    'total_price': booking[4],
                    'visit_date': booking[5],
                    'park_name': booking[6]
                }
            else:
                return None
    except sqlite3.Error as e:
        print(f"Ошибка при извлечении бронирования: {e}")
        return None


@app.route("/edit_booking", methods=["GET", "POST"])
def edit_booking():
    if request.method == "GET":
        park_name = request.args.get('park_name')  # Получаем имя парка из URL
        visit_date = request.args.get('visit_date')  # Получаем дату из URL
        
        # Получаем бронирование по park_name и visit_date
        booking = get_booking_by_park_and_date(park_name, visit_date)

        if not booking:
            flash("Не удалось найти нужное бронирование.", "error")
            return redirect(url_for('kab'))  # Перенаправляем в личный кабинет

        # Логируем, что мы получили из базы данных
        print(f"Полученные данные бронирования: {booking}")

        # Рассчитываем общую стоимость на сервере
        total_price = calculate_total_price(booking['adults_count'], booking['children_count'])

        # Передаем данные в шаблон
        return render_template("edit_booking.html", booking=booking, total_price=total_price)
    
    elif request.method == "POST":
        booking_id = request.form.get("booking_id")
        visit_date = request.form.get("visit_date")  # Получаем измененную дату
        adults_count = request.form.get("adults_count")
        children_count = request.form.get("children_count")

        # Рассчитываем общую стоимость на сервере
        total_price = calculate_total_price(int(adults_count), int(children_count))

        # Обновляем запись в базе данных, включая новую дату
        update_booking(booking_id, visit_date, adults_count, children_count, total_price)

        flash("Бронирование успешно обновлено.", "success")
        return redirect(url_for('kab'))  # Перенаправляем в личный кабинет
    
@app.route("/logout")
def logout():
    session.pop('user', None)
    flash("Вы успешно вышли из системы.", "info")
    return redirect(url_for('index'))

if __name__ == "__main__":
    # Создаём таблицы перед запуском сервера
    create_users_table()
    create_ticket_prices_table()
    create_bookings_table()  # Убедитесь, что эта строка есть
    app.run(debug=True)



