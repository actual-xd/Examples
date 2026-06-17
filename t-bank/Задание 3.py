test_cases = int(input())
for _ in range(test_cases):
    binary_string = input().strip()
    string_length = len(binary_string)

    if binary_string.count('1') == string_length:
        max_consecutive_ones = string_length
    else:
        doubled_string = binary_string + binary_string
        current_consecutive_ones = 0
        max_consecutive_ones = 0
        for char in doubled_string:
            if char == '1':
                current_consecutive_ones += 1
                if current_consecutive_ones > string_length:
                    current_consecutive_ones = string_length
                if current_consecutive_ones > max_consecutive_ones:
                    max_consecutive_ones = current_consecutive_ones
            else:
                current_consecutive_ones = 0

    max_rectangle_area = 0
    for rectangle_height in range(1, max_consecutive_ones + 1):
        rectangle_area = rectangle_height * (max_consecutive_ones - rectangle_height + 1)
        if rectangle_area > max_rectangle_area:
            max_rectangle_area = rectangle_area

    print(max_rectangle_area)
