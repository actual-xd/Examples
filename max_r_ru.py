board = [
    [1, 5, 1, -1],
    [3, 1, 2, 7],
    [3, 5, 2, 0],
]

def chess (board):

    rows_sum = [0] * len(board)
    cols_sum = [0] * len(board[0])

    for i in  range(len(board)):
        for j in range(len(board[0])):
            value = board[i][j]
            rows_sum[i] += value
            cols_sum[j] += value
    mm = float('-inf')

    for i in  range(len(board)):
        for j in range(len(board[0])):
            curr = rows_sum[i] +cols_sum[j]-board[i][j]*2
            if curr > mm :
                mm=curr

    return mm


print(chess(board))
