

#include <Adafruit_NeoMatrix.h>


#define MATRIX_PIN 6
#define MATRIX_WIDTH 8
#define MATRIX_HEIGHT 8

#define BTN_UP    2
#define BTN_DOWN  3
#define BTN_LEFT  4
#define BTN_RIGHT 5

Adafruit_NeoMatrix matrix = Adafruit_NeoMatrix(
  MATRIX_WIDTH, MATRIX_HEIGHT, MATRIX_PIN
);

int COLOR_SNAKE = matrix.Color(0, 200, 0);
int COLOR_HEAD  = matrix.Color(0, 255, 80);
int COLOR_FOOD  = matrix.Color(255, 30, 0);
int COLOR_BG    = matrix.Color(0, 0, 0);

#define MAX_LEN (MATRIX_WIDTH * MATRIX_HEIGHT)

struct Point { int x, y; };

Point snake[MAX_LEN];
int snakeLen = 3;

Point food;


int dir = 3;
int nextDir = 3;

unsigned long lastMove = 0;
unsigned long moveInterval = 400;

bool gameOver = false;
bool started  = false;


unsigned long lastBtnPress = 0;
const unsigned long DEBOUNCE_MS = 80;


void spawnFood() { // сделано
  bool occupied;
  do {
    occupied = false;
    food.x = random(0, MATRIX_WIDTH);
    food.y = random(0, MATRIX_HEIGHT);
    for (int i = 0; i < snakeLen; i++) {
      if (snake[i].x == food.x && snake[i].y == food.y) {
        occupied = true;
        break;
      }
    }
  } while (occupied);
}

void initGame() { // сделано
  snakeLen = 3;
  dir = 3; nextDir = 3;
  // Голова по центру, тело уходит влево
  snake[0] = {4, 4};
  snake[1] = {3, 4};
  snake[2] = {2, 4};
  spawnFood();
  moveInterval = 400;
  gameOver = false;
  lastMove = millis();
}

void drawGame() { // сделано
  matrix.fillScreen(COLOR_BG);

  matrix.drawPixel(food.x, food.y, COLOR_FOOD);

  for (int i = 1; i < snakeLen; i++) {
    matrix.drawPixel(snake[i].x, snake[i].y, COLOR_SNAKE);
  }

  matrix.drawPixel(snake[0].x, snake[0].y, COLOR_HEAD);
  matrix.show();
}

void drawGameOver() {

  for (int f = 0; f < 3; f++) {
    matrix.fillScreen(matrix.Color(180, 0, 0));
    matrix.show();
    delay(200);
    matrix.fillScreen(COLOR_BG);
    matrix.show();
    delay(200);
  }
}

void drawStartScreen() { // сделано

  matrix.fillScreen(COLOR_BG);
  int s[8] = {0b11111111,
                  0b11111111,
                  0b11111111,
                  0b11111111,
                  0b11111111,
                  0b11111111,
                  0b11111111,
                  0b11111111};
  for (int y = 0; y < 8; y++) {
    for (int x = 0; x < 8; x++) {
      if (s[y] & (1 << (7 - x))) {
        matrix.drawPixel(x, y, COLOR_HEAD);
      }
    }
  }
  matrix.show();
}

void readButtons() { // сделано
  if (millis() - lastBtnPress < DEBOUNCE_MS) return;

  if (digitalRead(BTN_UP) == LOW && dir != 1) {
    nextDir = 0; lastBtnPress = millis();
  } else if (digitalRead(BTN_DOWN) == LOW && dir != 0) {
    nextDir = 1; lastBtnPress = millis();
  } else if (digitalRead(BTN_LEFT) == LOW && dir != 3) {
    nextDir = 2; lastBtnPress = millis();
  } else if (digitalRead(BTN_RIGHT) == LOW && dir != 2) {
    nextDir = 3; lastBtnPress = millis();
  }
}

bool anyButtonPressed() {
  return (digitalRead(BTN_UP)    == LOW ||
          digitalRead(BTN_DOWN)  == LOW ||
          digitalRead(BTN_LEFT)  == LOW ||
          digitalRead(BTN_RIGHT) == LOW);
}

void moveSnake() { // snakmove
  dir = nextDir;
  Point newHead = snake[0];
  if (dir == 0) newHead.y--;
  else if (dir == 1) newHead.y++;
  else if (dir == 2) newHead.x--;
  else if (dir == 3) newHead.x++;

  // Проверка столкновения со стеной
  if (newHead.x < 0 || newHead.x >= MATRIX_WIDTH ||
      newHead.y < 0 || newHead.y >= MATRIX_HEIGHT) {
    gameOver = true;
    return;
  }

  // Проверка столкновения с собой
  for (int i = 0; i < snakeLen; i++) {
    if (snake[i].x == newHead.x && snake[i].y == newHead.y) {
      gameOver = true;
      return;
    }
  }

  // Проверка еды
  bool ate = (newHead.x == food.x && newHead.y == food.y);

  // Сдвиг тела
  if (ate) {
    // Добавляем сегмент — сдвигаем всё на 1
    if (snakeLen < MAX_LEN) snakeLen++;
    for (int i = snakeLen - 1; i > 0; i--) {
      snake[i] = snake[i - 1];
    }
  } else {
    for (int i = snakeLen - 1; i > 0; i--) {
      snake[i] = snake[i - 1];
    }
  }
  snake[0] = newHead;

  if (ate) {
    spawnFood();
    // Ускорение: минимум 120 мс
    if (moveInterval > 120) moveInterval -= 20;
  }
}

void setup() { // сделано
  pinMode(BTN_UP,    INPUT_PULLUP);
  pinMode(BTN_DOWN,  INPUT_PULLUP);
  pinMode(BTN_LEFT,  INPUT_PULLUP);
  pinMode(BTN_RIGHT, INPUT_PULLUP);

  matrix.begin();
  matrix.setBrightness(255);
  matrix.fillScreen(COLOR_BG);
  matrix.show();

  randomSeed(analogRead(A0));

  drawStartScreen();
  started = false;
}

void loop() {
  if (!started) {
    if (anyButtonPressed()) {
      delay(50); // ждём отпускания
      initGame();
      started = true;
    }
    return;
  }

  if (gameOver) {
    drawGameOver();
    drawStartScreen();
    started = false;
    return;
  }

  readButtons();

  unsigned long now = millis();
  if (now - lastMove >= moveInterval) {
    lastMove = now;
    moveSnake();
    if (!gameOver) {
      drawGame();
    }
  }
}
