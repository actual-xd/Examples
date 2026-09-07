from math import ceil

ans = 0

for x in range(1,1000):
    message = 9*x+8*ceil(x/8)
    if message <= 1024*8:
        ans = x
print(ans)
