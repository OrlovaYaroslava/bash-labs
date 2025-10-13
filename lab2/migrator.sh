#!/bin/bash

# Завершаем выполнение при любой ошибке
set -e

# 1. Загружаем переменные из файла .env
set -a 
source ../.env 
set +a 

# 2. Директория с миграциями
MIGRATIONS_DIR="./migrations"  

# Проверка существования директории с миграциями
if [ ! -d "$MIGRATIONS_DIR" ]; then
    echo "Ошибка: директория '$MIGRATIONS_DIR' не существует."
    exit 1
fi

# 3. Функции для выполнения SQL 
# Функция для выполнения SQL-запросов из файла
run_sql() {
    local file=$1
    echo "Выполняем SQL из файла: $file"
    PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USER" -d "$DB_NAME" -h "$DB_HOST" -p "$DB_PORT" -f "$file"
}

# Функция для выполнения SQL-запроса из строки
run_sql_c() {
    local query=$1
    PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USER" -d "$DB_NAME" -h "$DB_HOST" -p "$DB_PORT" -c "$query"
}

# 4. Создание таблицы migrations, если её нет
echo "Создаём таблицу 'migrations'."
run_sql_c "CREATE TABLE IF NOT EXISTS migrations (
    id SERIAL PRIMARY KEY,
    migration_name VARCHAR(255) UNIQUE NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);"

# 5. Получение списка уже применённых миграций
echo "Получаем список применённых миграций..."
applied_migrations=$(PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USER" -d "$DB_NAME" -h "$DB_HOST" -p "$DB_PORT" -t -c "SELECT migration_name FROM migrations;")

# 6. Применение новых миграций
echo "Применяем новые миграции..."
for file in "$MIGRATIONS_DIR"/*.sql; do
    # Проверяем, существует ли файл
    [ -e "$file" ] || continue

    migration_name=$(basename "$file")

    # Проверяем, была ли миграция уже применена
    if echo "$applied_migrations" | grep -q "$migration_name"; then
        echo "Миграция '$migration_name' уже применена"
    else
        # Если миграция не была применена, выполняем её
        echo "Применяем миграцию: '$migration_name'"
        run_sql "$file"
        # Записываем информацию о применённой миграции
        run_sql_c "INSERT INTO migrations (migration_name) VALUES ('$migration_name');"
        echo "Миграция '$migration_name' успешно применена"
    fi
done

echo "Все миграции обработаны"
