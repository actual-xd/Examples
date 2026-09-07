cache = {}

def F(n):
    if n in cache:
        return cache[n]

    if n < 4000:
        result = n
    elif n % 7 == 0:
        result = n + F(n // 7)
    else:
        result = 567 + F(n - 3)

    cache[n] = result
    return result

n = 4000
while True:
    if F(n) > 80000:
        print(n)  # Вывод: 62962
        break
    n += 1
