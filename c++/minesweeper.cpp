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
    int minesaround;
};


struct Board {
    int revealed_count;
    Cell grid [SIZE][SIZE];

    bool gameover;
    bool victory;

};


void init_board(Board& board) {
    for (int i=0; i<SIZE; i++){
        for (int j=0; j<SIZE; j++){
            board.grid [i][j].flagged = false;
            board.grid [i][j].mine = false;
            board.grid [i][j].revealed = false;
            board.grid [i][j].minesaround = false;
        }
    }
    board.revealed_count=0;
    board.gameover=false;
    board.victory=false;
    int count_mines=0;
    while (count_mines<MINES) {
       int x= rand() % SIZE;
       int y= rand() % SIZE;
       if (!board.grid[x][y].mine) {
            board.grid[x][y].mine=true;
            count_mines++;
       }
    }

    for (int i=0; i<SIZE; i++){
        for (int j=0; j<SIZE; j++){
            if(board.grid[i][j].mine){
                continue;
            }
            int mines=0;

            for (int di=-1; di <= 1; di++){
                for (int dj=-1; dj <= 1; dj++){
                    if (di==0 && dj==0){
                        continue;
                    }
                    int new_x = i+di;
                    int new_y = j+dj;

                    if (new_x>=0 && new_x<SIZE && new_y>=0 && new_y<SIZE){
                        if (board.grid[new_x][new_y].mine){
                            mines++;
                        }
                    }

                }
            }
            board.grid[i][j].minesaround=mines;
        }
    }
}


void reveal (int x, int y, Board& board) {

    if (x<0 || x>=SIZE || y<0 || y>=SIZE){
        return;
    }
    if (board.grid[x][y].flagged || board.grid[x][y].revealed){
        return;
    }
    board.grid[x][y].revealed=true;
    board.revealed_count++;

    if (board.grid[x][y].mine){
        board.gameover=true;
        return;
    }

    if (board.grid[x][y].minesaround==0){
         for (int di=-1; di <= 1; di++){
                for (int dj=-1; dj <= 1; dj++){
                    if (dj==0 && di==0){
                        continue;
                    }
                    reveal(x+di , y+dj , board);
             }
         }
    }
}


void toggle_flag(int x, int y, Board& board){

    if (board.grid[x][y].revealed) return;
    board.grid[x][y].flagged = !board.grid[x][y].flagged;
}

void display(const Board& board) {
    system(CLEAR);
    cout<< "   ";
    for (int i=0; i<SIZE; i++){
        cout<< (char)('A' + i)<< " ";
    }
    cout<<  "       Mines: " << MINES <<endl;
    for (int i=0; i < SIZE; i++){
        if (i + 1 < 10) cout << " ";
        cout<< i + 1 << " ";

        for (int j = 0; j < SIZE; j++) {
            if (board.gameover && board.grid[i][j].mine) {
                cout << MINE << " ";
            }
            else if (board.grid[i][j].flagged) {
                cout << FLAG << " ";
            }
            else if (!board.grid[i][j].revealed) {
                cout << CLOSED << " ";
            }
            else if (board.grid[i][j].mine) {
                cout << MINE << " ";
            }
            else if (board.grid[i][j].minesaround == 0) {
                cout << EMPTY << " ";
            }
            else {
                cout << board.grid[i][j].minesaround << " ";
            }
        }
        cout << endl;

    }
    cout << "Remaing safe cells: "<< SIZE*SIZE-MINES-board.revealed_count<<endl;

}

bool check_win (Board& board) {
    return board.revealed_count==SIZE*SIZE-MINES;
}



bool parse_input(const char* s, int& x, int& y, bool& flag_mode) {
    int len = strlen(s);
    if (len < 2 || len > 4) return false;

    flag_mode = false;

    if (s[len - 1] == 'F' || s[len - 1] == 'f') {
        flag_mode = true;
        len--;
    }

    char col = s[0];
    if (col >= 'a' && col <= 'z') col -= 32;
    if (col < 'A' && col >= 'A' + SIZE) return false;


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



int main () {
    srand(time(nullptr));

    Board board;
    init_board(board);

    cin.get();

    char input[10];

    while (!board.gameover &&  !board.victory) {
        display(board);

        cout << "> ";
        cin >> input;

        int x, y;
        bool flag_mode;

        if (!parse_input(input, x, y, flag_mode)) {
            cout << "Wrong input!" << endl;
            cin.get();
            continue;
        }

        if (flag_mode) {
            toggle_flag(x, y, board);
        }

        else {
            if (board.grid[x][y].flagged) {
                cout << "At first remove the flag!" << endl;
                 cin.get();
                 continue;
            }
            reveal(x,y,board);

            if (check_win(board)) {
                board.victory = true;
                board.gameover = false;
            }
        }
    }

    display(board);

    if (board.victory) {
        cout << "You win!" << endl;

    }
    else {
        cout << "Game over!" << endl;
    }


    return 0;
}
