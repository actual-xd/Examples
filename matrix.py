import random

n = int(input())
matrix = [[1]* n] * n

offset = 0

for i in range(n):
    for j in range(n):
        matrix[i][j] = random.randint(1,100)

for row in matrix:
    print(row)

while offset * 2 < n:
    s = 0
    start = offset
    end = n - offset - 1
    if start == end:
        s = matrix[start][end]
    else:
        # Верхняя сторона
        for j in range(start, end + 1):
            s += matrix[start][j]

        # Нижняя сторона
        for j in range(start, end + 1):
            s += matrix[end][j]

        # Левая сторона (без угла)
        for i in range(start + 1, end):
            s += matrix[i][start]

        # Правая сторона (без угла)
        for i in range(start + 1, end):
            s += matrix[i][end]
    print(f"Сумма периметра {offset} = {s}")
    offset += 1
