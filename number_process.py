n = int(input())

digits = ""
while n > 0:
    digits += (str(n % 6))
    n //= 6

print(digits[::-1])


l = [1, 0]
print(0 in l)
