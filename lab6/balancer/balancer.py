from flask import (
    Flask, request, jsonify, redirect,
    url_for, render_template_string
)
import requests
import threading
import time

app = Flask(__name__)

# Список всех инстансов (что мы добавили в пул)
instances = [
    "http://127.0.0.1:5001",
    "http://127.0.0.1:5002",
    "http://127.0.0.1:5003",
]

# Состояние инстансов: True - доступен, False - недоступен
instance_status = {url: True for url in instances}

# Индекс для алгоритма Round Robin
current_index = 0


def health_check():
    """
    Фоновая проверка состояния всех инстансов каждые 5 секунд.
    НИКАКИЕ инстансы из списка не удаляются,
    меняется только их статус в словаре instance_status.
    """
    while True:
        for inst in list(instances):
            try:
                resp = requests.get(f"{inst}/health", timeout=1)
                instance_status[inst] = (resp.status_code == 200)
            except Exception:
                instance_status[inst] = False

        time.sleep(5)


# Запускаем health-check в отдельном потоке
thread = threading.Thread(target=health_check, daemon=True)
thread.start()


def get_next_instance():
    """
    Алгоритм Round Robin:
    выбираем следующий ДОСТУПНЫЙ инстанс по кругу.
    Если доступных нет — вернём None.
    """
    global current_index

    if not instances:
        return None

    n = len(instances)
    for _ in range(n):
        inst = instances[current_index]
        current_index = (current_index + 1) % n

        if instance_status.get(inst):
            return inst

    return None


@app.route("/")
def index():
    """
    Web UI для управления пулом инстансов.

    1) Форма добавления нового инстанса (IP + порт).
    2) Список текущих инстансов с состоянием (доступен/недоступен).
    3) Кнопки удаления инстансов из списка (по индексу).
    """
    html = """
    <h2>Балансировщик нагрузки</h2>

    <h3>Текущие инстансы:</h3>
    <ul>
    {% for inst in instances %}
        <li>
            [{{ loop.index0 }}] {{ inst }} —
            {% if instance_status[inst] %}
                <span style="color: green;">доступен</span>
            {% else %}
                <span style="color: red;">недоступен</span>
            {% endif %}

            <!-- Кнопка удаления по индексу -->
            <form action="{{ url_for('remove_instance') }}"
                  method="post"
                  style="display:inline">
                <input type="hidden" name="index"
                       value="{{ loop.index0 }}">
                <button type="submit">Удалить</button>
            </form>
        </li>
    {% endfor %}
    </ul>

    <h3>Добавить новый инстанс</h3>
    <form action="{{ url_for('add_instance') }}" method="post">
        <label>IP:<br>
            <input name="ip" placeholder="127.0.0.1" required>
        </label><br><br>
        <label>Порт:<br>
            <input name="port" placeholder="5004" required>
        </label><br><br>
        <button type="submit">Добавить</button>
    </form>

    <h3>Отправить запрос на /process</h3>
    <form action="{{ url_for('process') }}" method="get">
        <button type="submit">Отправить</button>
    </form>
    """

    return render_template_string(
        html,
        instances=instances,
        instance_status=instance_status,
    )


@app.route("/add_instance", methods=["POST"])
def add_instance():
    """
    Добавление нового инстанса по IP и порту.
    Поля формы: ip, port.
    """
    ip = request.form.get("ip", "").strip()
    port = request.form.get("port", "").strip()

    if ip and port:
        url = f"http://{ip}:{port}"
        if url not in instances:
            instances.append(url)
            # По умолчанию считаем, что он недоступен,
            # пока health_check не проверит.
            instance_status[url] = False

    return redirect(url_for("index"))


@app.route("/remove_instance", methods=["POST"])
def remove_instance():
    """
    Удаление инстанса из пула по индексу (как в методичке).
    Индекс приходит из скрытого поля формы.
    """
    index_str = request.form.get("index", "").strip()

    if not index_str.isdigit():
        return redirect(url_for("index"))

    index = int(index_str)

    if 0 <= index < len(instances):
        url = instances.pop(index)
        instance_status.pop(url, None)

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
        resp = requests.get(f"{inst}/process", timeout=2)
        return jsonify({
            "balancer": "OK",
            "routed_to": inst,
            "instance_response": resp.json(),
        })
    except Exception:
        return jsonify(
            {"error": f"Ошибка соединения с {inst}"}
        ), 500


@app.route("/<path:path>", methods=["GET"])
def catch_all(path):
    """
    Перехватывает любые GET-запросы и перенаправляет их
    на доступный инстанс по Round Robin.
    """
    inst = get_next_instance()

    if not inst:
        return jsonify({"error": "Нет доступных инстансов"}), 503

    try:
        resp = requests.get(f"{inst}/{path}", timeout=2)
        return jsonify({
            "balancer": "OK",
            "routed_to": inst,
            "instance_response": resp.json(),
        })
    except Exception:
        return jsonify(
            {"error": f"Ошибка соединения с {inst}"}
        ), 500


if __name__ == "__main__":
    print("Балансировщик запущен на http://127.0.0.1:5000")
    app.run(port=5000, debug=True)
