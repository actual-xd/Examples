file = open("input.txt").read()


input = int(file)



temp = [None for x in range(10**7 + 1)]

def fib(n):
    if n <= 1:
        return n
    if temp[n] != None:
        return temp[n]
    temp[n] = fib(n-1) + fib(n-2)
    return temp[n]

output_file = open("output.txt", "w")
output_file.write(str(fib(input) % 10))
output_file.close()
