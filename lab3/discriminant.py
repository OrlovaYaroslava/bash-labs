def calculate_discriminant(a, b, c):
    """
    Вычисляет дискриминант квадратного уравнения ax^2 + bx + c = 0.

    Параметры:
        a (float или int): коэффициент при x^2
        b (float или int): коэффициент при x
        c (float или int): свободный член

    Возвращает:
        float: значение дискриминанта D = b^2 - 4ac
    """
    return b * b - 4 * a * c
