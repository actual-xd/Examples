c = 0
for line in open("9_47006.txt"):
    a = [int(x) for x in line.split()]
    a = sorted(a)
    if a[0] + a[1] > a[3] and a[0] + a[2] > a[3] and a[1] + a[2] > a[3]:
        c+=1





print(c)

