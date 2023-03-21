import json

def calc(q: dict) -> int:
    """Суммирует полученные от пользователя значения

    Args:
        q (dict): Словарь значений, полученный от пользователя. Содержит значения для подсчета суммы

    Returns:
        int: Сумма полученная в ходе подсчетов
    """
    sum_dict = 0
    for i in q.values():
        for j in i:
            try:
                k = int(j)
            except Exception:
                continue
            else:
                sum_dict += int(j)
    return sum_dict

def calc_file(file: bytes) -> int:
    """Конвертирует полученный файл и отправляет в метод calc для подсчёта значений

    Args:
        file (bytes): Bytes файл, полученный от пользователя. Содержит значения для подсчета суммы

    Returns:
        int: Сумма полученная в методе calc
    """
    sum_file = calc(json.loads(file.decode("UTF-8")))
    return sum_file