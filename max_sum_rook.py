board = [
    [1, 5, 1, -1],
    [3, 1, 2, 7],
    [3, 5, 2, 0],
]


def max_rook_sum(board: list[list[int]]) -> int:

    n = len(board)
    m = len(board[0])

    rows_sum = [0] * n
    cols_sum = [0] * m
    for i in range(n):
        for j in range(m):
            value = board[i][j]
            rows_sum[i] += value
            cols_sum[j] += value

    max_sum = 0
    for i in range(n):
        for j in range(m):
            curr_sum = rows_sum[i] + cols_sum[j] - board[i][j] * 2
            max_sum = max(max_sum, curr_sum)

    return max_sum

print(max_rook_sum(board))
