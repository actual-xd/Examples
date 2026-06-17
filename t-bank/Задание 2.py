input_string = input().strip()
string_length = len(input_string)
target_word_tbank = "tbank"
target_word_study = "study"
word_length = 5

cost_to_place_tbank = [0] * (string_length - word_length + 1)
for position in range(string_length - word_length + 1):
    mismatches = 0
    for char_index in range(word_length):
        if input_string[position + char_index] != target_word_tbank[char_index]:
            mismatches += 1
    cost_to_place_tbank[position] = mismatches

cost_to_place_study = [0] * (string_length - word_length + 1)
for position in range(string_length - word_length + 1):
    mismatches = 0
    for char_index in range(word_length):
        if input_string[position + char_index] != target_word_study[char_index]:
            mismatches += 1
    cost_to_place_study[position] = mismatches

prefix_min_study_cost = [10**9] * (string_length - word_length + 1)
suffix_min_study_cost = [10**9] * (string_length - word_length + 1)

if string_length - word_length + 1 > 0:
    prefix_min_study_cost[0] = cost_to_place_study[0]
    for position in range(1, string_length - word_length + 1):
        prefix_min_study_cost[position] = min(prefix_min_study_cost[position - 1], cost_to_place_study[position])

    suffix_min_study_cost[string_length - word_length] = cost_to_place_study[string_length - word_length]
    for position in range(string_length - word_length - 1, -1, -1):
        suffix_min_study_cost[position] = min(suffix_min_study_cost[position + 1], cost_to_place_study[position])

INF = float('inf')
minimum_total_cost = 10

for tbank_position in range(string_length - word_length + 1):

    best_non_overlapping_study_cost = INF
    if tbank_position >= word_length:
        best_non_overlapping_study_cost = min(best_non_overlapping_study_cost, prefix_min_study_cost[tbank_position - word_length])
    if tbank_position + word_length <= string_length - word_length:
        best_non_overlapping_study_cost = min(best_non_overlapping_study_cost, suffix_min_study_cost[tbank_position + word_length])

    if best_non_overlapping_study_cost < INF:
        minimum_total_cost = min(minimum_total_cost, cost_to_place_tbank[tbank_position] + best_non_overlapping_study_cost)


    for study_position in range(max(0, tbank_position - word_length + 1), min(string_length - word_length + 1, tbank_position + word_length)):

        words_compatible = True
        overlap_double_count_correction = 0

        overlap_start = max(tbank_position, study_position)
        overlap_end = min(tbank_position + word_length, study_position + word_length)

        for string_index in range(overlap_start, overlap_end):
            position_in_tbank = string_index - tbank_position
            position_in_study = string_index - study_position
            if target_word_tbank[position_in_tbank] != target_word_study[position_in_study]:
                words_compatible = False
                break
            if input_string[string_index] != target_word_tbank[position_in_tbank]:
                overlap_double_count_correction += 1

        if not words_compatible:
            continue

        total_cost = cost_to_place_tbank[tbank_position] + cost_to_place_study[study_position] - overlap_double_count_correction
        minimum_total_cost = min(minimum_total_cost, total_cost)

print(minimum_total_cost)
