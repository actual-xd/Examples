a = int(input())
s = 0
while a != 0:
    if 99 < a < 999 and a % 4 == 0:
        s += a
    a = int(input())
print(s)