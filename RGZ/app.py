from flask import Flask, request, jsonify
import re
from collections import Counter
import sys

app = Flask(__name__)

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
    most_common = [word for word, _ in freq.most_common(3)]
    
    return {
        "word_count": word_count,
        "most_frequent_words": most_common
    }

@app.route('/analyze', methods=['POST'])
def analyze():
    """Эндпоинт для анализа текста."""
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "Expected JSON with 'text' field"}), 400
    
    result = analyze_text(data['text'])
    return jsonify(result)

if __name__ == '__main__':
    # Поддержка запуска с указанием порта: python app.py 5001
    port = 5000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Порт должен быть целым числом. Используется порт по умолчанию: 5000")
    
    app.run(host='127.0.0.1', port=port, debug=False)