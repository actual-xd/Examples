low = 1
high = 1000
attempts = 0
guessed = False

while attempts < 10 and not guessed:
    guess = (low + high) // 2
    print(guess)

    response = input()
    if response == "Угадал!":
        guessed = True
    elif response == "Больше":
        low = guess + 1
    elif response == "Меньше":
        high = guess - 1

    attempts += 1