# Проверяем, передан ли аргумент
if [ $# -eq 0 ]; then
    echo "Ошибка: не указан файл."
    exit 1
fi

# Сохраняем имя файла
filename=$1

# Проверяем, существует ли файл
if [ ! -f "$filename" ]; then
    echo "Ошибка: файл '$filename' не существует."
    exit 1
fi

# Получаем статистику с помощью wc
lines=$(wc -l < "$filename")
words=$(wc -w < "$filename")
chars=$(wc -c < "$filename")

# Выводим результат
echo "Статистика для файла: $filename"
echo "Количество строк: $lines"
echo "Количество слов: $words"
echo "Количество символов: $chars"