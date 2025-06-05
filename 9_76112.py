c = 0
s = 0
mxc = 0
for line in open("9_76112.txt"):
    c+=1
    a = [int(x) for x in line.split()]
    np = [x for x in a if a.count(x) == 1]
    p = [x for x in a if a.count(x) > 1]
    if len(p) == 3:
        if len(np) > 0:
            if sum(np) / len(np) <= p[0]:
                if max(a) % min(a) != 0:
                    if sum(a) > s:
                        s = sum(a)
                        mxc = c
print(mxc)

