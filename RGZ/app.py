from flask import Flask, request, jsonify
import re
from collections import Counter
import sys
import json

app = Flask(__name__)

app.config['JSON_AS_ASCII'] = False  # Для корректного отображения кириллицы

def analyze_text(text: str):
    """
    Анализирует текст:
    - подсчитывает количество слов,
    - определяет топ-3 самых частых слов.
    """
    if not text or not text.strip():
        return {"word_count": 0, "most_frequent_words": []}
    
    # Извлекаем только слова, игнорируя пунктуацию, и приводим к нижнему регистру
    words = re.findall(r'\b\w+\b', text.lower())
    word_count = len(words)
    
    if word_count == 0:
        return {"word_count": 0, "most_frequent_words": []}
    
    # Определяем топ-3 самых частых слов
    freq = Counter(words)
    most_common = freq.most_common(3)
    
    # Форматируем результат: список кортежей [("слово", частота), ...]
    formatted_common = [[word, count] for word, count in most_common]
    
    return {
        "word_count": word_count,
        "most_frequent_words": formatted_common
    }

@app.route('/analyze', methods=['POST'])
def analyze():
    """Эндпоинт для анализа текста."""
    data = request.get_json()
    
    if not data or 'text' not in data:
        return jsonify({
            "error": "Expected JSON with 'text' field",
            "example": {"text": "ваш текст для анализа"}
        }), 400
    
    result = analyze_text(data['text'])
    
    # Используем json.dumps для полного контроля над кодировкой
    return app.response_class(
        response=json.dumps(result, ensure_ascii=False, indent=2),
        status=200,
        mimetype='application/json; charset=utf-8'
    )

@app.route('/health', methods=['GET'])
def health_check():
    """Эндпоинт для проверки работоспособности сервиса."""
    return jsonify({"status": "healthy", "service": "text-analyzer"})

@app.route('/')
def index():
    """Корневая страница с информацией о сервисе."""
    response_data = {
        "service": "Text Analyzer API",
        "version": "1.0",
        "endpoints": {
            "GET /health": "Проверка работоспособности",
            "POST /analyze": "Анализ текста",
            "POST /analyze (пример)": {
                "request": {"text": "ваш текст"},
                "response": {
                    "word_count": "число",
                    "most_frequent_words": "[['слово', частота], ...]"
                }
            }
        },
        "nginx_balancing": "Распределение между портами 5001, 5002, 5003"
    }
    
    # Возвращаем с правильной кодировкой
    return app.response_class(
        response=json.dumps(response_data, ensure_ascii=False, indent=2),
        status=200,
        mimetype='application/json; charset=utf-8'
    )

if __name__ == '__main__':
    # Поддержка запуска с указанием порта: python app.py 5001
    port = 5000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Порт должен быть целым числом. Используется порт по умолчанию: 5000")
    
    app.run(host='0.0.0.0', port=port, debug=False)