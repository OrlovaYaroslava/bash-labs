import pytest
from app import analyze_text

def test_normal_text():
    """Тест с обычным текстом."""
    result = analyze_text("Привет! Как дела? Привет, мир.")
    assert result["word_count"] == 5
    assert result["most_frequent_words"] == ["привет", "как", "дела"]

def test_empty_text():
    """Тест с пустым текстом."""
    result = analyze_text("")
    assert result["word_count"] == 0
    assert result["most_frequent_words"] == []

def test_whitespace_only():
    """Тест с пробелами и переносами."""
    result = analyze_text("   \n\t  ")
    assert result["word_count"] == 0
    assert result["most_frequent_words"] == []

def test_punctuation_and_case():
    """Тест с пунктуацией и разным регистром."""
    result = analyze_text("Привет! ПРИВЕТ, привет???")
    assert result["word_count"] == 3
    assert result["most_frequent_words"] == ["привет"]

def test_less_than_three_words():
    """Тест с 2 словами — не должно быть ошибки."""
    result = analyze_text("Привет мир")
    assert result["word_count"] == 2
    assert result["most_frequent_words"] == ["привет", "мир"]

def test_special_characters():
    """Тест с символами, не являющимися буквами."""
    result = analyze_text("Стоимость: 1000 р.! Или нет?")
    assert result["word_count"] == 5     # корректно
    assert "стоимость" in result["most_frequent_words"]
    assert "р" in result["most_frequent_words"]
