from functools import lru_cache
from math import factorial


@lru_cache(None)
def F(n):
    if n == 1:
        return 1
    else:
        return n * F(n - 1)


for i in range(1, 2050):
    F(i)

print(F(2023) / F(2020))
print(factorial(2023) / factorial(2020))
