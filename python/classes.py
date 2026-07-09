
class MyClass1:
    def __init__(self, param1, param2, param3):
        self.param1 = param1
        self.param2 = param2
        self.param3 = param3


    def print_values(self):
        print(self.param1)
        print(self.param2)
        print(self.param3)



def main():
    Class1Object = MyClass1(1,2,3)
    Class1Object.print_values()




if __name__ == "__main__":
    main()
