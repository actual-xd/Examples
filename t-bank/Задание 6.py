string_length, num_queries = map(int, input().split())
original_string = input().strip()

list_of_doubling_operations = []

for _ in range(num_queries):
    query_parameters = list(map(int, input().split()))

    if query_parameters[0] == 1:
        left_boundary, right_boundary = query_parameters[1], query_parameters[2]
        list_of_doubling_operations.append((left_boundary, right_boundary))

    else:

        query_position = query_parameters[1]
        current_position = query_position

        for operation_index in range(len(list_of_doubling_operations) - 1, -1, -1):
            operation_left, operation_right = list_of_doubling_operations[operation_index]
            segment_length = operation_right - operation_left + 1

            doubled_segment_end = operation_left + 2 * segment_length - 1

            if current_position < operation_left:
                continue

            elif current_position <= doubled_segment_end:
                offset_in_doubled_segment = current_position - operation_left
                current_position = operation_left + (offset_in_doubled_segment // 2)

            else:
                current_position = current_position - segment_length

        print(original_string[current_position - 1])
