s = 0
c = 0
a = int(input())


def f(n):
    b = ''
    while n > 0:
        b = str(n % 6) + b
        n = n // 6
    return b


while a != 0:
    if f(a)[-1] == '4':
        s += a
        c += 1
    a = int(input())
if c == 0:
    print("NO")
else:
    print(s / c)
