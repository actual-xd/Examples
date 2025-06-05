def f(n):
    return n > 1 and all(n % x != 0 for x in range(2, int(n ** 0.5) + 1))


for i in range(1_000_000, 1_001_000):
    divs = set()
    for u in range(1, int(i ** 0.5) + 1):
        if i % u == 0:
            if f(u):
                divs.add(u)
            if f(i // u):
                divs.add(i // u)


    if len(divs) == 3:
        print(i, max(divs))

