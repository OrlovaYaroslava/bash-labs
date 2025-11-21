from flask import (
    Flask, request, jsonify, redirect,
    url_for, render_template_string
)
import requests
import threading
import time

app = Flask(__name__)

# Активные серверные инстансы
instances = [
    "http://127.0.0.1:5001",
    "http://127.0.0.1:5002",
    "http://127.0.0.1:5003"
]

# Индекс для алгоритма Round Robin
current_index = 0


def health_check():
    """
    Фоновая проверка состояния всех инстансов каждые 5 секунд.
    Недоступные инстансы исключаются из списка.
    Восстановившиеся — возвращаются обратно.
    """
    global instances

    while True:
        alive = []

        for inst in instances:
            try:
                r = requests.get(f"{inst}/health", timeout=1)
                if r.status_code == 200:
                    alive.append(inst)
            except Exception:
                pass

        # Обновляем список только теми, кто ответил
        instances = alive

        time.sleep(5)


# Запуск фоновой проверки в отдельном потоке
thread = threading.Thread(target=health_check, daemon=True)
thread.start()


def get_next_instance():
    """
    Реализация Round Robin:
    возвращает следующий инстанс по кругу.
    """
    global current_index

    if not instances:
        return None

    inst = instances[current_index]
    current_index = (current_index + 1) % len(instances)

    return inst


@app.route("/")
def index():
    html = """
    <h2>Балансировщик нагрузки</h2>

    <h3>Текущие инстансы:</h3>
    <ul>
    {% for inst in instances %}
        <li>{{ inst }}</li>
    {% endfor %}
    </ul>

    <h3>Добавить новый инстанс</h3>
    <form action="/add_instance" method="post">
        <label>IP:<br>
            <input name="ip" placeholder="127.0.0.1" required>
        </label><br><br>
        <label>Порт:<br>
            <input name="port" placeholder="5004" required>
        </label><br><br>
        <button type="submit">Добавить</button>
    </form>

    <h3>Удалить инстанс</h3>
    <form action="/remove_instance" method="post">
        <label>IP:<br>
            <input name="ip" placeholder="127.0.0.1" required>
        </label><br><br>
        <label>Порт:<br>
            <input name="port" placeholder="5002" required>
        </label><br><br>
        <button type="submit">Удалить</button>
    </form>

    <h3>Отправить запрос на /process</h3>
    <form action="/process" method="get">
        <button type="submit">Отправить</button>
    </form>
    """
    return render_template_string(html, instances=instances)



@app.route("/add_instance", methods=["POST"])
def add_instance():
    """
    Добавление нового инстанса по IP и порту.
    """
    ip = request.form.get("ip", "").strip()
    port = request.form.get("port", "").strip()

    if ip and port:
        url = f"http://{ip}:{port}"
        if url not in instances:
            instances.append(url)

    return redirect(url_for("index"))


@app.route("/remove_instance", methods=["POST"])
def remove_instance():
    """
    Удаление инстанса из пула по IP и порту.
    """
    ip = request.form.get("ip", "").strip()
    port = request.form.get("port", "").strip()

    url = f"http://{ip}:{port}"

    if url in instances:
        instances.remove(url)

    return redirect(url_for("index"))


@app.route("/process")
def process():
    """
    Отправляет запрос клиента на активный инстанс
    по алгоритму Round Robin.
    """
    inst = get_next_instance()

    if not inst:
        return jsonify({"error": "Нет доступных инстансов"}), 503

    try:
        r = requests.get(f"{inst}/process", timeout=2)
        return jsonify({
            "balancer": "OK",
            "routed_to": inst,
            "instance_response": r.json()
        })
    except Exception:
        return jsonify({"error": f"Ошибка соединения с {inst}"}), 500


@app.route("/<path:path>", methods=["GET"])
def catch_all(path):
    """
    Универсальный маршрут.
    Перехватывает любые GET-запросы и перенаправляет их на инстанс.
    """

    inst = get_next_instance()

    if not inst:
        return jsonify({"error": "Нет доступных инстансов"}), 503

    try:
        r = requests.get(f"{inst}/{path}", timeout=2)
        return jsonify({
            "balancer": "OK",
            "routed_to": inst,
            "instance_response": r.json()
        })
    except Exception:
        return jsonify({"error": f"Ошибка соединения с {inst}"}), 500


if __name__ == "__main__":
    print("Балансировщик запущен на http://127.0.0.1:5000")
    app.run(port=5000, debug=True)
