c = 0
for line in open("9_59778.txt"):
    a = [int(x) for x in line.split()]
    p = [x for x in a if a.count(x) > 1]
    np = [x for x in a if a.count(x) == 1]
    if len(p) == 4:
        if sum(np) / len(np) > sum(p):
            c += 1

print(c)
