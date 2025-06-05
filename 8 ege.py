from itertools import product, permutations

words = set(permutations("АМФИБРАХИЙ"))
word = list(permutations("АМФИБРАХИЙ"))
print(len(word), len(words))

c = 0
for word in words:

    if word[4] == "Б" and word[5] == "Р":
        c+=1

print(c)

