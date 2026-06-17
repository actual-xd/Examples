array_size = int(input())
array_elements = list(map(int, input().split()))

result_for_each_element = []
distinct_values_in_array = set(array_elements)

for index in range(array_size):
    current_element = array_elements[index]

    count_greater_elements = sum(1 for element in array_elements if element > current_element)
    count_smaller_elements = sum(1 for element in array_elements if element < current_element)

    count_distinct_greater = sum(1 for value in distinct_values_in_array if value > current_element)
    count_distinct_smaller = sum(1 for value in distinct_values_in_array if value < current_element)

    if count_distinct_greater > 0 and count_distinct_smaller > 0:
        answer_for_element = count_distinct_greater + count_distinct_smaller + 1
    else:
        answer_for_element = max(count_greater_elements, count_smaller_elements)

    result_for_each_element.append(answer_for_element)

print(' '.join(map(str, result_for_each_element)))
