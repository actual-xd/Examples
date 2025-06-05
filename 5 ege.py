def f(n):
    b = ''
    while n > 0:
        b = str(n % 3) + b
        n = n // 3
    return b

a = []
for N in range(1, 2031):
    r = f(3 ** 100 - N)

    a.update({r.count('0'): N})

print(a)
