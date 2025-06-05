c = 0

for line in open("9_48430.txt"):
    a = [int(x) for x in line.split()]
    np = [x for x in a if a.count(x) == 1]
    p = [x for x in a if a.count(x) > 1]
    if len(set(a)) == 4 and len(np) == 2:
        if sum(set(p)) < sum(np):
            c+=1
print(c)




