counter = 0

nums = []
for line in open('9_.txt'):
    a = [int(x) for x in line.split()]
    for x in a:
        nums.append(x)

for line in open('9_.txt'):
    a = [int(x) for x in line.split()]

    for x in set(a):
        if nums.count(x) == 46 and a.count(x) == 1:
            counter += 1
            break

print(counter)
