for i in range(106_000_000, 107_000_000):

    divs = set()
    for u in range(1, int(i**0.5) + 1):
        if i % u == 0:
            if u % 2 == 0:
                divs.add(u)
            if i // u % 2 == 0:
                divs.add(i // u)
            if len(divs) > 3:
                break

    if len(divs) == 3:
        print(i)

