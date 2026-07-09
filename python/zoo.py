class Animal:
    def __init__(self, legs):
        self.legs = legs


class Tiger(Animal):
    def __init__(self, sound, fur=True):
        super().__init__(4)
        self.sound = sound
        self.fur = fur

    def print_legs(self):
        print(self.legs)

    def make_sound(self):
        print(self.sound)



class Bird(Animal):
    def __init__(self, sound, feathers=True):
        super().__init__(2)
        self.sound = sound
        self.feathers = feathers

    def print_legs(self):
        print(self.legs)

    def make_sound(self):
        print(self.sound)



def main():

    animals = [
        Bird("Чирик!"),
        Bird("КУ-КА-РЕ-КУ"),
        Tiger("Ррррр")
    ]




    print(animals[2].feathers)

if __name__ == "__main__":
    main()
