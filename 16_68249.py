
max_diff = 0
args = []

cache = {0: 0}

def F(n):
    if n in cache:
        return cache[n]
    if n % 2 == 1:
        cache[n] = F(n  -   1 ) + 2 * n -1
    else:
        cache[n] = 4 * F(n // 2)
    return cache[n]


for a in range(1, 1000):
    F_a = F(a)
    for b in range(1, 1000):
        F_b = F(b)
        if F_a - F_b == 1001:
            diff = a - b
            if diff > max_diff:
                max_diff = diff


print(max_diff)
