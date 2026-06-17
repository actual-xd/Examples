#include <iostream>
#include <cstdlib>
#include <ctime>
#include <conio.h>
#include <windows.h>

using namespace std;

const int WIDTH = 40;
const int HEIGHT = 20;
const int RACKET_SIZE = 4;

const char WALL = '#';
const char BALL = '*';
const char RACKET = '|';
const char EMPTY = ' ';

struct Ball {
    int x;
    int y;
    int dx;
    int dy;
};

struct Racket {
    int y;
};

struct Board {
    char grid[HEIGHT][WIDTH];
    Ball ball;
    Racket left_racket;
    Racket right_racket;
    int left_score;
    int right_score;
    bool game_over;
};

void init_board(Board& board) {
    for (int i = 0; i < HEIGHT; i++) {
        for (int j = 0; j < WIDTH; j++) {
            if (i == 0 || i == HEIGHT - 1 || j == 0 || j == WIDTH - 1) {
                board.grid[i][j] = WALL;
            } else {
                board.grid[i][j] = EMPTY;
            }
        }
    }

    board.ball.x = WIDTH / 2;
    board.ball.y = HEIGHT / 2;
    board.ball.dx = (rand() % 2 == 0) ? 1 : -1;
    board.ball.dy = (rand() % 2 == 0) ? 1 : -1;

    board.left_racket.y = HEIGHT / 2 - RACKET_SIZE / 2;
    board.right_racket.y = HEIGHT / 2 - RACKET_SIZE / 2;

    board.left_score = 0;
    board.right_score = 0;
    board.game_over = false;
}

void clear_playing_field(Board& board) {
    for (int i = 1; i < HEIGHT - 1; i++) {
        for (int j = 1; j < WIDTH - 1; j++) {
            board.grid[i][j] = EMPTY;
        }
    }
}

void place_rackets(Board& board) {
    for (int i = 0; i < RACKET_SIZE; i++) {
        int left_y = board.left_racket.y + i;
        int right_y = board.right_racket.y + i;
        if (left_y > 0 && left_y < HEIGHT - 1) {
            board.grid[left_y][1] = RACKET;
        }
        if (right_y > 0 && right_y < HEIGHT - 1) {
            board.grid[right_y][WIDTH - 2] = RACKET;
        }
    }
}

void place_ball(Board& board) {
    board.grid[board.ball.y][board.ball.x] = BALL;
}

void display(const Board& board) {
    system("cls");

    cout << "Left: " << board.left_score << "  Right: " << board.right_score << endl;

    for (int i = 0; i < HEIGHT; i++) {
        for (int j = 0; j < WIDTH; j++) {
            cout << board.grid[i][j];
        }
        cout << endl;
    }

    cout << "W/S - left, I/K - right, Q - quit" << endl;
}

void move_rackets(Board& board, char input) {
    if (input == 'w' || input == 'W') {
        if (board.left_racket.y > 2) {
            board.left_racket.y--;
        }
    }
    if (input == 's' || input == 'S') {
        if (board.left_racket.y + RACKET_SIZE < HEIGHT - 2) {
            board.left_racket.y++;
        }
    }
    if (input == 'i' || input == 'I') {
        if (board.right_racket.y > 2) {
            board.right_racket.y--;
        }
    }
    if (input == 'k' || input == 'K') {
        if (board.right_racket.y + RACKET_SIZE < HEIGHT - 2) {
            board.right_racket.y++;
        }
    }
}

void move_ball(Board& board) {
    board.grid[board.ball.y][board.ball.x] = EMPTY;

    board.ball.x += board.ball.dx;
    board.ball.y += board.ball.dy;

    if (board.ball.y <= 1 || board.ball.y >= HEIGHT - 2) {
        board.ball.dy = -board.ball.dy;
        board.ball.y += board.ball.dy;
    }

    if (board.ball.x <= 2 && board.ball.dx < 0) {
        int relative_y = board.ball.y - board.left_racket.y;
        if (relative_y >= 0 && relative_y < RACKET_SIZE) {
            board.ball.dx = -board.ball.dx;
            board.ball.x = 3;
        }
    }

    if (board.ball.x >= WIDTH - 3 && board.ball.dx > 0) {
        int relative_y = board.ball.y - board.right_racket.y;
        if (relative_y >= 0 && relative_y < RACKET_SIZE) {
            board.ball.dx = -board.ball.dx;
            board.ball.x = WIDTH - 4;
        }
    }

    if (board.ball.x < 1) {
        board.right_score++;
        if (board.right_score == 5) {
            board.game_over = true;
        }
        board.ball.x = WIDTH / 2;
        board.ball.y = HEIGHT / 2;
        board.ball.dx = (rand() % 2 == 0) ? 1 : -1;
        board.ball.dy = (rand() % 2 == 0) ? 1 : -1;
    }

    if (board.ball.x >= WIDTH - 1) {
        board.left_score++;
        if (board.left_score == 5) {
            board.game_over = true;
        }
        board.ball.x = WIDTH / 2;
        board.ball.y = HEIGHT / 2;
        board.ball.dx = (rand() % 2 == 0) ? 1 : -1;
        board.ball.dy = (rand() % 2 == 0) ? 1 : -1;
    }

    if (board.ball.y < 1) board.ball.y = 1;
    if (board.ball.y >= HEIGHT - 1) board.ball.y = HEIGHT - 2;
}

int main() {
    srand(time(nullptr));

    Board board;
    init_board(board);

    cout << "Ping Pong! First to 5 wins." << endl;
    cout << "W/S - left racket, I/K - right racket, Q - quit" << endl;
    cout << "Press Enter to start...";
    cin.get();

    char input = 0;
    bool quit = false;

    while (!quit && !board.game_over) {
        if (_kbhit()) {
            input = _getch();
            if (input == 'q' || input == 'Q') {
                quit = true;
            }
            move_rackets(board, input);
        }

        move_ball(board);
        clear_playing_field(board);
        place_rackets(board);
        place_ball(board);
        display(board);

        Sleep(50);
    }

    if (board.game_over) {
        if (board.left_score == 5) {
            cout << "Left player wins!" << endl;
        } else {
            cout << "Right player wins!" << endl;
        }
    }

    cout << "Final score " << "leftscore= "<< board.left_score << "   rightscore= "<< board.right_score<< endl;

    return 0;
}
