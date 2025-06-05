def f(x, y, string):
    if x > y:
        return 0
    if x == y:
        return 1
    if string.count('A') > 2:
        return 0
    else:
        return f(x - 2, y, string + "A") + f(x * 2, y, string + "B") + f(x * 3, y, string + "C")


print(f(6, 48, ""))


def u(x, y):
    if x == y:
        return 1
    if x > y:
        return 0
    else:
        return u(int(str(x), 2) + 1, y) + u(bin(str(x) + str(bin(int(str(x), 2) % 5)[::2]))[::2], y)


print(u(1, 101000101))
