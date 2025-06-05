from fnmatch import fnmatch



for i in range(519, 10**13+1, 519):
    if fnmatch(str(i), '32*54?123'):
        if len(str(i)) % 2 == 0:
            left = str(i)[0:len(str(i))//2]
            left_sum = sum([int(x) for x in left])
            right = str(i)[len(str(i))//2:len(str(i))]
            right_sum = sum([int(x) for x in right])
            if left_sum == right_sum:
                print(i, i // 519)