#код 1
def _send_message(connection_info, recipient, content_type, content):
    print(f"Connecting to {connection_info}...")
    print(f"Sending {content_type} to {recipient} with {content}...")
    print(f"{content_type.capitalize()} sent.")

def send_email(to, subject, body):
    _send_message("SMTP server", to, "email", f"subject '{subject}'")

def send_sms(to, message):
    _send_message("SMS gateway", to, "sms", f"message '{message}'")

#код 2
def calculate_order_total(items):
    return sum(item["price"] * item["quantity"] for item in items)

def process_payment():
    print("Processing payment...")
    print("Payment successful!")

def send_confirmation_email():
    print("Sending confirmation email...")

def process_order(order):
    items = order["items"]
    order_total = calculate_order_total(items)
    print(f"Total: {order_total}")
    process_payment()
    send_confirmation_email()
    print("Order complete.")

#код 3
# Правила доставки: (country, weight < 5) → стоимость
SHIPPING_RULES = {
    ("USA", True): 10,
    ("USA", False): 20,
    ("Canada", True): 15,
    ("Canada", False): 25,
    ("Other", True): 30,
    ("Other", False): 50,
}

def calculate_shipping(country, weight):
    key = (country if country in ("USA", "Canada") else "Other", weight < 5)
    return SHIPPING_RULES[key]

#код 4
# Налоговые ставки и пороги (в рублях)
TAX_BRACKET_1_LIMIT = 10_000
TAX_BRACKET_2_LIMIT = 20_000
TAX_RATE_1 = 0.10   
TAX_RATE_2 = 0.15   
TAX_RATE_3 = 0.20   

def calculate_tax(income):
    """Рассчитывает налог на доход с учётом прогрессивной шкалы."""
    if income <= TAX_BRACKET_1_LIMIT:
        return income * TAX_RATE_1
    elif income <= TAX_BRACKET_2_LIMIT:
        return income * TAX_RATE_2
    else:
        return income * TAX_RATE_3
    
#код 5
def create_report(employee_data):
    """
    Формирует отчёт по сотруднику.
    Ожидает словарь с ключами: name, age, department, salary, bonus, performance_score.
    """
    print(f"Name: {employee_data['name']}")
    print(f"Age: {employee_data['age']}")
    print(f"Department: {employee_data['department']}")
    print(f"Salary: {employee_data['salary']}")
    print(f"Bonus: {employee_data['bonus']}")
    print(f"Performance Score: {employee_data['performance_score']}")

# Пример вызова:
# employee = {"name": "Иван", "age": 30, "department": "IT", ...}
# create_report(employee)