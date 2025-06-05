string = ">" + "1"*10 + "2" * 20 + "3" * 30

while ">1" in string or ">2" in string or ">3" in string:
    if ">1" in string:
        string = string.replace(">1", "22>", 1)
    if ">2" in string:
        string =string.replace(">2", "2>", 1)
    if ">3" in string:
        string =string.replace(">3", "1>", 1)
print(string)

print(string.count("3")*3 + string.count("2")*2 + string.count("1"))

print()

