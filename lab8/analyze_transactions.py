import asyncio
import json
import os
import glob

# Папка с транзакциями (должна совпадать с generate_transactions.py)
TRANSACTIONS_DIR = "transactions"

# Лимит для предупреждения (в рублях)
EXPENSE_LIMIT = 10000.0

async def read_transaction_file(filepath):
    """Асинхронно читает один файл с транзакциями."""
    # Имитация асинхронной операции ввода-вывода
    await asyncio.sleep(0.01)
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

async def analyze_transactions():
    """Основная функция анализа."""
    # Ищем все JSON-файлы в папке transactions/
    pattern = os.path.join(TRANSACTIONS_DIR, "transactions_part_*.json")
    filepaths = glob.glob(pattern)

    if not filepaths:
        print(f"Нет файлов транзакций в папке '{TRANSACTIONS_DIR}'")
        return

    print(f"Найдено файлов: {len(filepaths)}. Начинаю анализ...")

    # Словарь для агрегации
    category_totals = {}

    # Читаем все файлы асинхронно 
    for filepath in sorted(filepaths):
        transactions = await read_transaction_file(filepath)
        for tx in transactions:
            cat = tx["category"]
            amount = tx["amount"]
            category_totals[cat] = category_totals.get(cat, 0) + amount

    # Выводим результаты и проверяем лимиты
    print("\nИтоговые расходы по категориям:")
    print("-" * 40)
    for category, total in category_totals.items():
        print(f"{category:15} : {total:10.2f} ₽")
        if total > EXPENSE_LIMIT:
            print(f"ВНИМАНИЕ: расходы в категории \"{category}\" превысили лимит! Сумма: {total:.2f} ₽")

    print("\nАнализ завершён.")

def main():
    if not os.path.exists(TRANSACTIONS_DIR):
        print(f"Папка '{TRANSACTIONS_DIR}' не найдена. Сначала запустите generate_transactions.py")
        return

    asyncio.run(analyze_transactions())

if __name__ == "__main__":
    main()