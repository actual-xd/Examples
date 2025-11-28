count = int(input())
total_sum = 0

for _ in range(count):
    number = int(input())
    while number > 0:
        total_sum += number % 10
        number //= 10

print(total_sum)
