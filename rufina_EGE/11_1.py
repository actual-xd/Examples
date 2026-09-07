cache = {}


def F(n):
    if n in cache:
        return cache[n]
    if n >= 2025:
        return n
    else:
        cache[n] = n + F(n + 2)


for i in range(2026, 1, -1):
    F(i)


print(cache[2022] - cache[2023])
