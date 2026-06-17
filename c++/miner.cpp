#include <iostream>
#include <cstdlib>
#include <ctime>
#include <cstring>

#define CLEAR "cls"


using namespace std;

const int SIZE = 10;
const int MINES = 15;

const char CLOSED = '#';
const char FLAG = 'F';
const char MINE = '*';
const char EMPTY = '.';

struct Cell {
    bool mine;
    bool revealed;
    bool flagged;
    int adjacent_mines;
};

struct Board {
    Cell grid[SIZE][SIZE];
    int revealed_count;
    bool game_over;
    bool win;
};

void init_board(Board& board) {
    for (int i = 0; i < SIZE; i++) {
        for (int j = 0; j < SIZE; j++) {
            board.grid[i][j].mine = false;
            board.grid[i][j].revealed = false;
            board.grid[i][j].flagged = false;
            board.grid[i][j].adjacent_mines = 0;
        }
    }
    board.revealed_count = 0;
    board.game_over = false;
    board.win = false;

    int placed = 0;
    while (placed < MINES) {
        int x = rand() % SIZE;
        int y = rand() % SIZE;
        if (!board.grid[x][y].mine) {
            board.grid[x][y].mine = true;
            placed++;
        }
    }

    for (int i = 0; i < SIZE; i++) {
        for (int j = 0; j < SIZE; j++) {
            if (board.grid[i][j].mine) continue;
            int count = 0;
            for (int di = -1; di <= 1; di++) {
                for (int dj = -1; dj <= 1; dj++) {
                    if (di == 0 && dj == 0) continue;
                    int ni = i + di;
                    int nj = j + dj;
                    if (ni >= 0 && ni < SIZE && nj >= 0 && nj < SIZE) {
                        if (board.grid[ni][nj].mine) count++;
                    }
                }
            }
            board.grid[i][j].adjacent_mines = count;
        }
    }
}

void reveal(Board& board, int x, int y) {
    if (x < 0 || x >= SIZE || y < 0 || y >= SIZE) return;
    if (board.grid[x][y].revealed || board.grid[x][y].flagged) return;

    board.grid[x][y].revealed = true;
    board.revealed_count++;

    if (board.grid[x][y].mine) {
        board.game_over = true;
        return;
    }

    if (board.grid[x][y].adjacent_mines == 0) {
        for (int di = -1; di <= 1; di++) {
            for (int dj = -1; dj <= 1; dj++) {
                if (di == 0 && dj == 0) continue;
                reveal(board, x + di, y + dj);
            }
        }
    }
}

void toggle_flag(Board& board, int x, int y) {
    if (board.grid[x][y].revealed) return;
    board.grid[x][y].flagged = !board.grid[x][y].flagged;
}

void display(const Board& board) {
    system(CLEAR);

    cout << "   ";
    for (int j = 0; j < SIZE; j++) {
        cout << (char)('A' + j) << ' ';
    }
    cout << "    Mines: " << MINES << endl;

    for (int i = 0; i < SIZE; i++) {
        if (i + 1 < 10) cout << ' ';
        cout << i + 1 << ' ';

        for (int j = 0; j < SIZE; j++) {
            const Cell& cell = board.grid[i][j];

            if (board.game_over && cell.mine) {
                cout << MINE << ' ';
            } else if (cell.flagged) {
                cout << FLAG << ' ';
            } else if (!cell.revealed) {
                cout << CLOSED << ' ';
            } else if (cell.mine) {
                cout << MINE << ' ';
            } else if (cell.adjacent_mines == 0) {
                cout << EMPTY << ' ';
            } else {
                cout << cell.adjacent_mines << ' ';
            }
        }
        cout << endl;
    }

    int remaining = SIZE * SIZE - board.revealed_count - MINES;
    cout << "Remaining safe cells: " << remaining << endl;
}

bool parse_input(const char* s, int& x, int& y, bool& flag_mode) {
    int len = strlen(s);
    if (len < 2 || len > 4) return false;

    flag_mode = false;

    if (s[len - 1] == 'F' || s[len - 1] == 'f') {
        flag_mode = true;
        len--;
        if (len < 2) return false;
    }

    char col = s[0];
    if (col >= 'a' && col <= 'z') col -= 32;
    if (col < 'A' || col >= 'A' + SIZE) return false;

    int row = 0;
    for (int i = 1; i < len; i++) {
        if (s[i] < '0' || s[i] > '9') return false;
        row = row * 10 + (s[i] - '0');
    }
    if (row < 1 || row > SIZE) return false;

    x = row - 1;
    y = col - 'A';
    return true;
}

bool check_win(Board& board) {
    return board.revealed_count == SIZE * SIZE - MINES;
}

int main() {
    srand(time(nullptr));

    Board board;
    init_board(board);

    cout << "Minesweeper!" << endl;
    cout << "Commands:" << endl;
    cout << "  E3  - reveal cell" << endl;
    cout << "  E3F - toggle flag" << endl;
    cout << "Press Enter to start...";
    cin.get();

    char input[10];

    while (!board.game_over && !board.win) {
        display(board);
        cout << "> ";
        cin >> input;

        int x, y;
        bool flag_mode;

        if (!parse_input(input, x, y, flag_mode)) {
            cout << "Invalid input! Use: E3 or E3F" << endl;
            cin.get();
            continue;
        }

        if (flag_mode) {
            toggle_flag(board, x, y);
        } else {
            if (board.grid[x][y].flagged) {
                cout << "Remove flag first!" << endl;
                cin.get();
                continue;
            }
            reveal(board, x, y);

            if (check_win(board)) {
                board.win = true;
                board.game_over = false;
            }
        }
    }

    display(board);

    if (board.win) {
        cout << "You win!" << endl;
    } else {
        cout << "Game over." << endl;
    }

    return 0;
}
