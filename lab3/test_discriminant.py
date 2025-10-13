import unittest
from discriminant import calculate_discriminant


class TestDiscriminant(unittest.TestCase):
    """Тесты для функции вычисления дискриминанта."""

    def test_positive_discriminant(self):
        """Положительный тест: D > 0."""
        result = calculate_discriminant(1, -5, 6) 
        self.assertEqual(result, 1.0)

    def test_zero_discriminant(self):
        """Положительный тест: D = 0."""
        result = calculate_discriminant(1, -2, 1)  
        self.assertEqual(result, 0.0)

    def test_negative_discriminant(self):
        """Негативный тест: D < 0."""
        result = calculate_discriminant(1, 1, 1)  
        self.assertEqual(result, -3.0)


if __name__ == "__main__":
    unittest.main()