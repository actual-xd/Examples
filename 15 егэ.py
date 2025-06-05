
arr = []
for x in range(0, 100):
    for y in range(0, 100):
        for i in range(0, 100):
            if (((x in arr) is (x^2 <= 81)) and ((y^2 <= 36) is (y in arr))):
                arr.append(i)


print(set(arr))
