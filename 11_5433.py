import math

one_serial = (5536*1024*8)/23155
print(one_serial)

for i in range(1, 100):
    if not (one_serial >= i * 377):
        print(i)