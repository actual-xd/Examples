#include <iostream>
#include <cstdlib>
#include <ctime>
#include <cstring>

using namespace std;

const int SIZE = 10;
const int MAX_SHIPS = 10;
const int MAX_POSITIONS;


const char WAVE = '~';
const char VERTICAL = '|';
const char HORIZONTAL = '-';
const char HIT = 'X';
const char MISS = 'O';

struct Ship {
    int size;
    int hit_count;
    int pos_count;
    int positions[MAX_POSITIONS][2];
    int hits[MAX_POSITIONS][2];
};


struct Board {
    char grid[SIZE][SIZE];
    Ship ships[MAX_SHIPS];
    int ships_count;
    bool shots[SIZE][SIZE];
};


struct Player {
    Board board;
};


void init_board(Board& board){
    for (int i=0; i<SIZE; i++){
        for (int j=0; j<SIZE; j++){
            board.grid[i][j]=WAVE;
            board.shots [i][j]=false;
        }
    }
    board.ships_count=0;
}

bool can_place(Board& board, int x, int y, int size, bool horizontal){
    if (horizontal){
        if (y+size>SIZE) return false;
        for (int i = -1; i <= 1; i++) {
            for (int j = -1; j <= size; j++) {
                int new_x = x + i;
                int new_y = y + j;
                if (new_y>=0 && new_y<SIZE && new_x>=0 && new_x>SIZE){
                    if (board.grid[new_x][new_y]!=WAVE) return false;
                }
            }
        }
    }
    else{
       if (x+size>SIZE) return false;
        for (int i = -1; i <= 1; i++) {
            for (int j = -1; j <= size; j++) {
                int new_x = x + j;
                int new_y = y + i;
                if (new_y>=0 && new_y<SIZE && new_x>=0 && new_x>SIZE){
                    if (board.grid[new_x][new_y]!=WAVE) return false;
                }
            }
        }
    }
    return true;
}

void random_placement(Player& player){
    int ship_sizes[MAX_SHIPS] = [4,3,3,2,2,2,1,1,1,1]
    for (int i=0; i<MAX_SHIPS; i++){
        int size=ship_sizes[i];
        bool placed=false;
        while (!placed){
            bool horizontal = rand() % 2;
            int x = rand() % SIZE;
            int y = rand() % SIZE;
            if (can_place (player.board, x, y, size, horizontal)){
                place_ship(player.board, x, y, size, horizontal);
                placed=true;
            }

        }
    }
}



void place_ship(Board& board, int x, int y, int size, bool horizontal) {
    Ship& ship = board.ships[board.ships_count];
    ship.size=size;
    ship.hit_count = 0;
    ship.pos_count = 0;

    if (horizontal) {
        for (int i = y; i < y + size; i++) {
            board.grid[x][i]=HORIZONTAL;
            ship.positions[ship.pos_count][0] = x;
            ship.positions[ship.pos_count][1] = i;
            ship.pos_count++;

        }
    }
    else{
        for (int i=x; i<x+size; i++){
            board.grid[i][y]=VERTICAL;
            ship.positions[ship.pos_count][0] = i;
            ship.positions[ship.pos_count][1] = y;
            ship.pos_count++;
        }
    }
    board.ships_count++;

}


bool all_sunk(Board& board) {
    for (int i=0; i<ships_count; i++){
        if (board.ships[i].hit_count != board.ships[i].size) return false;
    }
    return true;
}

void display(Board& board, bool hide_ships) {
    cout << "   ";
    for (int i=0; i<SIZE; i++){
        cout <<  (char)('A' + i) << " ";
    }
    cout<<endl;
    for (int i=0; i<SIZE; i++){
        cout<< i + 1 << " ";
        for (int j = 0; j<SIZE; j++) {
            char cell = board.grid[i][j];
            if (hide_ships && (cell == HORIZONTAL || cell == VERTICAL)) {
                cout << WAVE << " ";
            }
            else {
                cout << cell << " ";
            }
        }
        cout << endl;
    }
}

void show_boards(Player& human, Player& bot) {
    cout<< endl;
    cout<< "доска игрока: "<< endl;

    display(human.board, false);
    cout<< endl;
    cout<< "доска бота: " << endl;
    display (bot.board, true);
    cout<<endl;
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


bool parse_coords(const char* s, int& x, int& y) {
    int len = strlen(s);
    if (len < 2 || len > 3) return false;
    char col = s[0];
    if (col >= 'a' && col <= 'j') col -= 32;
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


bool is_in_positions(Ship& ship, int x, int y) {
    for (int i = 0; i < ship.pos_count; i++) {
        if (ship.positions[i][0] == x && ship.positions[i][1] == y) return true;
    }
    return false;
}


void human_turn(Player& human, PLayer& bot) {
    char input[10];
    while (true) {
        show_boards(human, bot);
        cout << "Введите координаты: ";
        cin >> input;

        int x, y;
        if (!parse_coords(input, x, y)) {
            cout << "Координаты плохие!" << endl;
            continue;
        }
        int result = recieve_shot(bot.board, x, y);
        if (result == -1) {
            cout << "Сюда уже стреляли" << endl;
        }
        else if (result == 0) {
            cout << "Мимо" << endl;
            show_boards(human, bot);
            break;
        }
        else if (result == 1) {
            cout << "Попал!" << endl;
            if (all_sunk(bot.board)) {
                show_boards(human, bot);
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

        cout << "Робот стреляет сюда:  " << (char)('A' + y) << x + 1 << endl;

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


int main () {
    srand(time(nullptr));


    Player bot;
    Player human;
    init_board(bot.board);
    init_board(human.board);

    random_placement(human);
    random_placement(robot);

    while (true) {
        human_turn(human, bot);
        if (all_sunk(bot.board)) {
            cout << "Ты выиграл!" << endl;
            break;
        }
        robot_turn(human, bot);
        if (all_sunk(human.board)) {
            cout << "Бот выиграл!" << endl;
            break;
        }
    }

    return 0;
}
