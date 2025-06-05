s = 0
n = 0
m = 0

for line in open("9.txt"):
    n += 1
    a = [int(x) for x in line.split()]
    p = [x for x in a if a.count(x) > 1]
    np = [x for x in a if a.count(x) == 1]
    a = sorted(a)
    if len(p) == 3:
        if sum(np)/4 <= p[0]:
            if a[6] % a[0] != 0:
                if sum(a) > s:
                    s = sum(a)
                    m = n

print(m)