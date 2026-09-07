cache = {}

def F(n):
    if n in cache:
        return cache[n]
    if n < 3:
        cache[n] = 1
    else:
        s = 0
        for i in range(1, n):
            s += F(i)
        cache[n] = s
    return cache[n]

print(F(18))
