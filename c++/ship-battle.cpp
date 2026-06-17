#include <iostream>
#include <cstdlib>
#include <ctime>
#include <cstring>

using namespace std;

const int SIZE = 10;
const int MAX_SHIPS = 10;
const int MAX_POSITIONS = 4;

const char WAVE = '~';
const char VERTICAL = '|';
const char HORIZONTAL = '-';
const char HIT = 'X';
const char MISS = 'O';

struct Ship {
    int size;
    int positions[MAX_POSITIONS][2];
    int pos_count;
    int hits[MAX_POSITIONS][2];
    int hit_count;
};

struct Board {
    char grid[SIZE][SIZE];
    Ship ships[MAX_SHIPS];
    int ship_count;
    bool shots[SIZE][SIZE];
};

void init_board(Board& board) {
    for (int i = 0; i < SIZE; i++) {
        for (int j = 0; j < SIZE; j++) {
            board.grid[i][j] = WAVE;
            board.shots[i][j] = false;
        }
    }
    board.ship_count = 0;
}

bool can_place(Board& board, int x, int y, int size, bool horizontal) {
    if (horizontal) {
        if (y + size > SIZE) return false;
        for (int i = -1; i <= 1; i++) {
            for (int j = -1; j <= size; j++) {
                int nx = x + i;
                int ny = y + j;
                if (nx >= 0 && nx < SIZE && ny >= 0 && ny < SIZE) {
                    if (board.grid[nx][ny] != WAVE) return false;
                }
            }
        }
    } else {
        if (x + size > SIZE) return false;
        for (int i = -1; i <= size; i++) {
            for (int j = -1; j <= 1; j++) {
                int nx = x + i;
                int ny = y + j;
                if (nx >= 0 && nx < SIZE && ny >= 0 && ny < SIZE) {
                    if (board.grid[nx][ny] != WAVE) return false;
                }
            }
        }
    }
    return true;
}

void place_ship(Board& board, int x, int y, int size, bool horizontal) {
    Ship& ship = board.ships[board.ship_count];
    ship.size = size;
    ship.pos_count = 0;
    ship.hit_count = 0;

    if (horizontal) {
        for (int j = y; j < y + size; j++) {
            board.grid[x][j] = HORIZONTAL;
            ship.positions[ship.pos_count][0] = x;
            ship.positions[ship.pos_count][1] = j;
            ship.pos_count++;
        }
    } else {
        for (int i = x; i < x + size; i++) {
            board.grid[i][y] = VERTICAL;
            ship.positions[ship.pos_count][0] = i;
            ship.positions[ship.pos_count][1] = y;
            ship.pos_count++;
        }
    }
    board.ship_count++;
}

bool is_in_positions(Ship& ship, int x, int y) {
    for (int i = 0; i < ship.pos_count; i++) {
        if (ship.positions[i][0] == x && ship.positions[i][1] == y) return true;
    }
    return false;
}

bool is_in_hits(Ship& ship, int x, int y) {
    for (int i = 0; i < ship.hit_count; i++) {
        if (ship.hits[i][0] == x && ship.hits[i][1] == y) return true;
    }
    return false;
}

void mark_surrounding(Board& board, Ship& ship) {
    for (int p = 0; p < ship.pos_count; p++) {
        int x = ship.positions[p][0];
        int y = ship.positions[p][1];
        for (int i = -1; i <= 1; i++) {
            for (int j = -1; j <= 1; j++) {
                int nx = x + i;
                int ny = y + j;
                if (nx >= 0 && nx < SIZE && ny >= 0 && ny < SIZE) {
                    if (!is_in_positions(ship, nx, ny) && !board.shots[nx][ny]) {
                        board.grid[nx][ny] = MISS;
                        board.shots[nx][ny] = true;
                    }
                }
            }
        }
    }
}

int receive_shot(Board& board, int x, int y) {
    if (board.shots[x][y]) return -1;
    board.shots[x][y] = true;
    char cell = board.grid[x][y];

    if (cell == WAVE) {
        board.grid[x][y] = MISS;
        return 0;
    }
    if (cell == HORIZONTAL || cell == VERTICAL) {
        board.grid[x][y] = HIT;
        for (int s = 0; s < board.ship_count; s++) {
            Ship& ship = board.ships[s];
            if (is_in_positions(ship, x, y)) {
                ship.hits[ship.hit_count][0] = x;
                ship.hits[ship.hit_count][1] = y;
                ship.hit_count++;
                if (ship.hit_count == ship.size) {
                    mark_surrounding(board, ship);
                    return 2;
                }
                return 1;
            }
        }
    }
    return -1;
}

bool all_sunk(Board& board) {
    for (int i = 0; i < board.ship_count; i++) {
        if (board.ships[i].hit_count != board.ships[i].size) return false;
    }
    return true;
}

void display(Board& board, bool hide_ships) {
    cout << "   ";
    for (int j = 0; j < SIZE; j++) {
        cout << (char)('A' + j) << ' ';
    }
    cout << endl;

    for (int i = 0; i < SIZE; i++) {
        if (i + 1 < 10) cout << ' ';
        cout << i + 1 << ' ';
        for (int j = 0; j < SIZE; j++) {
            char cell = board.grid[i][j];
            if (hide_ships && (cell == HORIZONTAL || cell == VERTICAL)) {
                cout << WAVE << ' ';
            } else {
                cout << cell << ' ';
            }
        }
        cout << endl;
    }
}

struct Player {
    Board board;
};

void random_placement(Player& player) {
    int ship_sizes[MAX_SHIPS] = {4, 3, 3, 2, 2, 2, 1, 1, 1, 1};
    for (int s = 0; s < MAX_SHIPS; s++) {
        int size = ship_sizes[s];
        bool placed = false;
        while (!placed) {
            bool horizontal = rand() % 2;
            int x = rand() % SIZE;
            int y = rand() % SIZE;
            if (can_place(player.board, x, y, size, horizontal)) {
                place_ship(player.board, x, y, size, horizontal);
                placed = true;
            }
        }
    }
}

bool parse_coords(const char* s, int& x, int& y) {
    int len = strlen(s);
    if (len < 2 || len > 3) return false;
    char col = s[0];
    if (col >= 'a' && col <= 'z') col -= 32;
    if (col < 'A' || col > 'J') return false;

    int row = 0;
    for (int i = 1; i < len; i++) {
        if (s[i] < '0' || s[i] > '9') return false;
        row = row * 10 + (s[i] - '0');
    }
    if (row < 1 || row > 10) return false;

    x = row - 1;
    y = col - 'A';
    return true;
}

void show_boards(Player& human, Player& robot) {
    cout << endl << "доска игрока: " << endl;
    display(human.board, false);
    cout << endl << "доска бота: " << endl;
    display(robot.board, true);
}

void human_turn(Player& human, Player& robot) {
    char input[10];
    while (true) {
        show_boards(human, robot);
        cout << "Введите координаты: ";
        cin >> input;

        int x, y;
        if (!parse_coords(input, x, y)) {
            cout << "Координаты плохие" << endl;
            continue;
        }

        int result = receive_shot(robot.board, x, y);
        if (result == -1) {
            cout << "Сюда уже стреляли" << endl;
            continue;
        }
        if (result == 0) {
            cout << "Мимо!" << endl;
            show_boards(human, robot);
            break;
        } else if (result == 1) {
            cout << "Попал!" << endl;
            if (all_sunk(robot.board)) {
                show_boards(human, robot);
                break;
            }
        } else {
            cout << "Убил!" << endl;
            if (all_sunk(robot.board)) {
                show_boards(human, robot);
                break;
            }
        }
    }
}

void robot_turn(Player& human, Player& robot) {
    while (true) {
        int available[SIZE * SIZE][2];
        int count = 0;
        for (int i = 0; i < SIZE; i++) {
            for (int j = 0; j < SIZE; j++) {
                if (!human.board.shots[i][j]) {
                    available[count][0] = i;
                    available[count][1] = j;
                    count++;
                }
            }
        }
        if (count == 0) return;

        int idx = rand() % count;
        int x = available[idx][0];
        int y = available[idx][1];

        cout << "Робот стреляет сюда: " << (char)('A' + y) << x + 1 << endl;

        int result = receive_shot(human.board, x, y);
        if (result == 0) {
            cout << "Он промахнулся" << endl;
            show_boards(human, robot);
            break;
        } else if (result == 1) {
            cout << "Робот попал" << endl;
            if (all_sunk(human.board)) {
                show_boards(human, robot);
                break;
            }
        } else {
            cout << "Робот потопил корабль!" << endl;
            if (all_sunk(human.board)) {
                show_boards(human, robot);
                break;
            }
        }
    }
}

int main() {
    srand(time(nullptr));

    Player human;
    Player robot;

    init_board(human.board);
    init_board(robot.board);

    random_placement(human);
    random_placement(robot);

    while (true) {
        human_turn(human, robot);
        if (all_sunk(robot.board)) {
            cout << "Ты выиграл!" << endl;
            break;
        }
        robot_turn(human, robot);
        if (all_sunk(human.board)) {
            cout << "Бот выиграл!" << endl;
            break;
        }
    }

    return 0;
}
