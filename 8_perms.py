from itertools import product
import re

count = 0


a = "0123456789"

for i in product(a, repeat=4):
    s = "".join(i)
    if len(set(s)) == 4 and (s[0] != "0"):
        results = []
        for g in range(len(s) - 1):
            results.append(int(s[g]) % 2 != int(s[g + 1]) % 2)

        if all(results):
            count += 1
print(count)

