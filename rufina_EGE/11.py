cache = {1: 1}

def F(n):
    if n == 1:
        return 1
    elif n in cache:
        return cache[n]
    else:
        cache[n] = n * F(n - 1)

    return cache[n]

for i in range(1, 2025):
    F(i)

result = (cache[2024] - cache[2023]) / cache[2022]
print(result)
