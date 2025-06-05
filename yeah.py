

xd = {}

for i in range(84052, 84130 + 1):
    arr = set()
    for t in range(1, round(i ** 0.5) + 1):
        if i % t == 0:
            arr.add(t)
            arr.add(i // t)
    xd[i] = len(arr)



for u in xd:


    if xd.get(u) == 72:
        print(u)
        break
