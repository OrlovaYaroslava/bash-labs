from flask import Flask, jsonify
import sys

app = Flask(__name__)

# 1. Получение номера порта при запуске

if len(sys.argv) != 2:
    print("Ошибка: необходимо указать порт, например:")
    print("python app_instance.py 5001")
    sys.exit(1)

PORT = int(sys.argv[1])


@app.route("/health")
def health():
    """Маршрут проверки состояния инстанса."""
    return jsonify({
        "status": "OK",
        "instance": PORT
    })


@app.route("/process")
def process():
    """Маршрут обработки основных запросов."""
    return jsonify({
        "message": "Запрос обработан",
        "instance": PORT
    })


if __name__ == "__main__":
    print(f"Запуск серверного инстанса на порту {PORT}")
    app.run(host="127.0.0.1", port=PORT)
