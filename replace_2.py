arr = set()

for i in range(10, 1000 + 1):
    s = bin(i)[2:]
    s = s[s.index("1") + 1:]
    s = s.lstrip("0")

    if s == "":
        s = "0"
    r = int(s, 2)
    temp = r - i
    arr.add(temp)

print(len(arr))


s = "12345"
print(s.index("2"))
