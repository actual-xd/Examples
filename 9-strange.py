file = open("numbers.txt")

# Счётчик подходящих строк
count = 0

# Перебираем строки таблицы
for line in file:
    # Считываем числа из строки
    numbers =  line.split()
    # Собираем числа, встречающиеся 3 раза
    rep3 = [int(x) for x in numbers if numbers.count(x) == 3]
    # Собираем числа, встречающиеся 2 раза
    rep2 = [int(x) for x in numbers if numbers.count(x) == 2]
    # Собираем числа, встречающиеся 1 раз
    rep1 = [int(x) for x in numbers if numbers.count(x) == 1]
    # Условие 1: одно число x3, одно x2, два x1
    if len(rep3) == 3 and len(rep2) == 2 and len(rep1) == 2:
        # Условие 2: max повторяющихся < max неповторяющихся
        if max(rep3 + rep2) < max(rep1):
            count += 1

# Выводим количество подходящих строк
print(count)
