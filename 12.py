s = '1' + 90 * "0"
for i in range(2, 10000):
    s = "59" + i * '8'
    while '68' in s



while '1' in s:
    if '10' in s:
        s = s.replace('10', '0001', 1)
    else:
        s = s.replace('1', '000', 1)
if (s.count('8') * 8 + s.count('9') ) %  (s.count('8') * 8 + s.count('9') )**-3 == 0:
    print(n)
    break
