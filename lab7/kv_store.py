import json
import os
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

# ------------------------------------------------------
# 1. Корректный путь к data.json, чтобы он был внутри lab7/
# ------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data.json")

# ------------------------------------------------------
# 2. Загрузка данных при старте
# ------------------------------------------------------
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
else:
    data = {}  # если файла нет — создаём пустой словарь


def save_data():
    """Сохранение словаря data в файл data.json."""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Ошибка при сохранении данных: {e}")

# ------------------------------------------------------
# 3. Настройка Flask-Limiter
# ------------------------------------------------------

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["100 per day"]  # общий лимит для всех маршрутов
)

# ------------------------------------------------------
# 4. API методов key-value хранилища
# ------------------------------------------------------

@app.route("/set", methods=["POST"])
@limiter.limit("10 per minute")
def set_value():
    """Сохранить ключ-значение"""
    content = request.json

    if not content or "key" not in content or "value" not in content:
        return jsonify({"error": "Expected JSON: {key, value}"}), 400

    key = content["key"]
    value = content["value"]

    data[key] = value
    save_data()

    return jsonify({"status": "OK", "saved": {key: value}})


@app.route("/get/<key>", methods=["GET"])
def get_value(key):
    """Получить значение по ключу"""
    if key not in data:
        return jsonify({"error": "Key not found"}), 404

    return jsonify({"key": key, "value": data[key]})


@app.route("/delete/<key>", methods=["DELETE"])
@limiter.limit("10 per minute")
def delete_value(key):
    """Удалить ключ"""
    if key not in data:
        return jsonify({"error": "Key not found"}), 404

    removed_value = data.pop(key)
    save_data()

    return jsonify({"status": "deleted", "key": key, "value": removed_value})


@app.route("/exists/<key>", methods=["GET"])
def exists(key):
    """Проверить наличие ключа"""
    return jsonify({
        "key": key,
        "exists": key in data
    })

# ------------------------------------------------------
# 5. Запуск приложения
# ------------------------------------------------------

if __name__ == "__main__":
    print("Key-value хранилище запущено на http://127.0.0.1:5000")
    app.run(debug=True)
