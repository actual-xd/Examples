file = open("input.txt").readlines()
stack = []
for i in range(len(file)):
    file[i] = file[i].strip()

m = int(file[0])

commands = file[1:]

output_file = open("output.txt", "w")
for i in range(m):
    if commands[i][0] == "+":
        stack.append(commands[i][2:])
    elif commands[i][0] == "-":
        output_file.write(str(stack[-1]) + "\n")
        stack.pop()

output_file.close()
