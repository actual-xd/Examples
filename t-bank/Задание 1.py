input_string = input().strip()
digit_counts = [0] * 10
for char in input_string:
    digit_counts[int(char)] += 1

for digit in range(1, 10):
    if digit_counts[digit] > 0:
        first_nonzero_digit = digit
        digit_counts[digit] -= 1
        break

output_parts = [str(first_nonzero_digit)]
for digit in range(10):
    if digit_counts[digit]:
        output_parts.append(str(digit) * digit_counts[digit])

print("".join(output_parts))
