number = int(input())

s = 0
while number != 0:
    if number % 4 == 0 and len(str(number)) == 3:
        s += number
    number = int(input())
print(s)