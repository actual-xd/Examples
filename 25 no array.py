for i in range(106000000, 107000000 + 1):
    count = 1
    sqrtI = round(i ** 0.5)
    if i % 2 == 0:
        for j in range(2, sqrtI + 1):
            if i % j == 0:
                if j % 2 == 0:
                    count += 1
            if i % j == 0:
                if (i // j) % 2 == 0:
                    count += 1
            if (j * j == i) and (j % 2 == 0):
                count -= 1
            if count > 3:
                break
    if count == 3:
        print(i)
        count = 1