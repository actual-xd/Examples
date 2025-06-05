a = int(input())
b = int(input())
c = (b - a) // 2
if a % 2 == 1 or b % 2 == 1:
    c += 1
print(c)

