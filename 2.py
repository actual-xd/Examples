print("x y z w")
for x in 0, 1:
    for y in 0, 1:
        for z in 0, 1:
            for w in 0, 1:
                f = ((w <= (not x)) == (z <= y)) and (y or w)
                if f == 1:
                    print(x, y, z, w)
