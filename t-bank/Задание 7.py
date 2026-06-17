MOD = 10**9 + 7
n, k = map(int, input().split())
if k > 2 * n - 2:
    print(0)
black_diagonal_lengths = []
white_diagonal_lengths = []
for diagonal_offset in range(-(n-1), n):
    diagonal_length = n - abs(diagonal_offset)
    if diagonal_offset % 2 == 0:
        black_diagonal_lengths.append(diagonal_length)
    else:
        white_diagonal_lengths.append(diagonal_length)
black_diagonal_lengths.sort()
white_diagonal_lengths.sort()
def compute_placement_dp(diagonal_lengths, max_bishops_allowed):
    num_diagonals = len(diagonal_lengths)
    dp_ways = [0]*(num_diagonals+1)
    dp_ways[0] = 1
    for diagonal_index, diagonal_length in enumerate(diagonal_lengths):
        for num_rooks in range(min(diagonal_index+1, max_bishops_allowed), 0, -1):
            dp_ways[num_rooks] = (dp_ways[num_rooks] + dp_ways[num_rooks-1] * (diagonal_length - (num_rooks-1))) % MOD
    return dp_ways
dp_black_placements = compute_placement_dp(black_diagonal_lengths, n)
dp_white_placements = compute_placement_dp(white_diagonal_lengths, n-1)
total_ways = 0
max_black_rooks = len(black_diagonal_lengths)
max_white_rooks = len(white_diagonal_lengths)
for black_rooks_count in range(k+1):
    if black_rooks_count <= max_black_rooks and k-black_rooks_count <= max_white_rooks:
        total_ways = (total_ways + dp_black_placements[black_rooks_count] * dp_white_placements[k-black_rooks_count]) % MOD

print(total_ways)
