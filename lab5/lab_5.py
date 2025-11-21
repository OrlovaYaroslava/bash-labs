from flask import Flask, request, redirect, url_for
from flask_login import (
    LoginManager, UserMixin,
    login_user, logout_user, login_required, current_user
)
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os


# 1. Загрузка .env
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "dev-fallback-key")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///lab5/database.db")

# 2. Создание приложения Flask
app = Flask(__name__)
app.secret_key = SECRET_KEY

# 3. Настройка базы данных SQLite
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# 4. Настройка менеджера авторизации
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# 5. Модель пользователя
class User(db.Model, UserMixin):
    """Класс пользователя."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<User {self.email}>"


# 6. Создание таблицы пользователей
with app.app_context():
    db.create_all()
    # добавляем администратора, если его нет
    if not User.query.filter_by(email="admin@example.com").first():
        admin = User(
            email="admin@example.com",
            password="1234",
            name="Администратор"
        )
        db.session.add(admin)
        db.session.commit()


# 7. Восстановление пользователя по ID
@login_manager.user_loader
def load_user(user_id):
    """Загрузка пользователя по его ID."""
    return db.session.get(User, int(user_id))


# 8. Главная страница
@app.route("/")
@login_required
def index():
    """Главная страница доступна только авторизованным пользователям."""
    return f"""
        <h1>Лабораторная работа №5</h1>
        <h3>Тема: Реализация аутентификации и авторизации пользователей</h3>
        <p>
            В данной лабораторной работе демонстрируются процессы регистрации,
            входа и выхода пользователей с использованием пакета
            <b>Flask-Login</b> и базы данных SQLite.
        </p>
        <p><b>Вы вошли как:</b> {current_user.name} ({current_user.email})</p>
        <form action="{url_for('logout')}" method="get">
            <button type="submit">Выйти</button>
        </form>
    """


# 9. Страница входа
@app.route("/login", methods=["GET", "POST"])
def login():
    """Обработка входа пользователя."""
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()

        if not user:
            return _login_form(
                error="Пользователь с таким email не найден.", email=email
            )
        if user.password != password:
            return _login_form(error="Неверный пароль.", email=email)

        login_user(user)
        return redirect(url_for("index"))

    email_prefill = request.args.get("email", "")
    return _login_form(email=email_prefill)


def _login_form(error: str = "", email: str = "") -> str:
    """Форма входа."""
    err_html = f'<p style="color:red">{error}</p>' if error else ""
    return f"""
        <h2>Вход</h2>
        {err_html}
        <form method="post">
            <label>Email:<br>
                <input type="email" name="email" value="{email}" required>
            </label><br><br>
            <label>Пароль:<br>
                <input type="password" name="password" required>
            </label><br><br>
            <button type="submit">Войти</button>
        </form>
        <p>Нет аккаунта?
            <a href="{url_for('signup')}">Зарегистрироваться</a>

    """


# 10. Страница регистрации
@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Обработка регистрации нового пользователя."""
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or not password:
            return _signup_form("Все поля обязательны.")
        if User.query.filter_by(email=email).first():
            return _signup_form("Пользователь с таким email уже существует.")

        new_user = User(email=email, password=password, name=name)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login", email=email))

    return _signup_form()


def _signup_form(error: str = "") -> str:
    """Форма регистрации."""
    err_html = f'<p style="color:red">{error}</p>' if error else ""
    return f"""
        <h2>Регистрация</h2>
        {err_html}
        <form method="post">
            <label>Имя:<br>
                <input type="text" name="name" required>
            </label><br><br>
            <label>Email:<br>
                <input type="email" name="email" required>
            </label><br><br>
            <label>Пароль:<br>
                <input type="password" name="password" required>
            </label><br><br>
            <button type="submit">Зарегистрироваться</button>
        </form>
        <p>Уже есть аккаунт?
            <a href="{url_for('login')}">Войти</a>
        </p>
    """


# 11. Выход
@app.route("/logout")
@login_required
def logout():
    """Завершение сессии пользователя."""
    logout_user()
    return redirect(url_for("login"))


# 12. Просмотр пользователей (для отладки)
@app.route("/users")
def list_users():
    """Отображение списка пользователей."""
    users = User.query.all()
    html = "<h3>Пользователи:</h3><ul>"
    for user in users:
        html += f"<li>{user.id}: {user.name} — {user.email}</li>"
    html += "</ul>"
    return html


# 13. Запуск приложения
if __name__ == "__main__":
    app.run(debug=True)
