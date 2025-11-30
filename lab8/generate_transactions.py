import asyncio
import json
import random
from datetime import datetime
import sys
import os

# Категории трат (можно расширить)
CATEGORIES = ["еда", "транспорт", "развлечения", "одежда", "здоровье"]

# Папка для сохранения файлов
OUTPUT_DIR = "transactions"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_transaction():
    """Генерирует одну транзакцию."""
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "category": random.choice(CATEGORIES),
        "amount": round(random.uniform(100, 5000), 2)
    }

async def save_batch(batch, batch_number):
    """Асинхронно сохраняет пачку транзакций в файл."""
    filename = f"{OUTPUT_DIR}/transactions_part_{batch_number}.json"
    # Имитация асинхронной операции ввода-вывода
    await asyncio.sleep(0.01)  # небольшая задержка для демонстрации асинхронности
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(batch, f, ensure_ascii=False, indent=2)
    print(f"Сохранено {len(batch)} транзакций в файл {filename}")

async def generate_transactions(total_count: int):
    """Основная асинхронная функция генерации."""
    batch = []
    batch_number = 1

    for i in range(total_count):
        # Генерация одной транзакции
        transaction = generate_transaction()
        batch.append(transaction)

        # Если набрали 10 — сохраняем
        if len(batch) == 10:
            await save_batch(batch, batch_number)
            batch = []
            batch_number += 1

    # Сохраняем остаток, если он есть (например, при 105 транзакциях)
    if batch:
        await save_batch(batch, batch_number)

def main():
    if len(sys.argv) != 2:
        print("Использование: python generate_transactions.py <количество_транзакций>")
        sys.exit(1)

    try:
        total = int(sys.argv[1])
        if total <= 0:
            raise ValueError
    except ValueError:
        print("Ошибка: укажите положительное целое число.")
        sys.exit(1)

    print(f"Генерация {total} транзакций...")
    asyncio.run(generate_transactions(total))
    print("Генерация завершена.")

if __name__ == "__main__":
    main()