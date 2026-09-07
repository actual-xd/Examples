
cache_F = {0: 0}
cache_G = {0: 0}

def G(n):
    if n in cache_G:
        return cache_G[n]
    if n >= 395881:
        cache_G[n] = n / 6 + 34
    else:
        cache_G[n] = 13 + G(n + 39)
    return cache_G[n]


def F(n):
    if n in cache_F:
        return cache_F[n]
    if n >= 25:
        cache_F[n] = F(n - 5) + 5580
    else:
        cache_F[n] = 12 * (G(n - 11) - 14)
    return cache_F[n]


for i in range(396000, 1, -1):
    G(i)


print(F(937))
