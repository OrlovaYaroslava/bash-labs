def calculate_discriminant(a, b, c):
    """
    Вычисляет дискриминант квадратного уравнения ax^2 + bx + c = 0.

    Параметры:
        a (int или float): коэффициент при x^2
        b (int или float): коэффициент при x
        c (int или float): свободный член

    """
    if not all(isinstance(x, (int, float)) for x in (a, b, c)):
        raise TypeError("Все аргументы должны быть числами (int или float).")
    return float(b * b - 4 * a * c)    
