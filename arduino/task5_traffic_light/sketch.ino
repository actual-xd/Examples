/*
  Лабораторная работа 5: Светофор с кнопкой
  
  Автоматический светофор работает в обычном режиме:
    Красный → Жёлтый → Зелёный → Жёлтый → Красный ...

  При нажатии кнопки включается режим "мигания" (жёлтый мигает) —
  имитация ночного/аварийного режима светофора.
  Повторное нажатие возвращает в автоматический режим.
  Текущий режим сохраняется в EEPROM.
*/

#include <EEPROM.h>

// Пины светодиодов
#define PIN_RED    9
#define PIN_YELLOW 10
#define PIN_GREEN  11

// Пин кнопки
#define PIN_BUTTON 2

// EEPROM адрес для хранения режима
#define EEPROM_MODE_ADDR 0

// Режимы работы
#define MODE_AUTO  0  // Автоматический светофор
#define MODE_BLINK 1  // Мигание жёлтым

// Фазы автоматического светофора
#define PHASE_RED         0
#define PHASE_RED_YELLOW  1
#define PHASE_GREEN       2
#define PHASE_YELLOW      3

// Длительности фаз (мс)
const unsigned long phaseDuration[] = {
  3000,  // Красный
  1000,  // Красный + Жёлтый
  3000,  // Зелёный
  1000   // Жёлтый
};

const unsigned long BLINK_INTERVAL = 500; // Интервал мигания (мс)

// --- Переменные состояния ---
int currentMode  = MODE_AUTO;
int lastMode     = MODE_AUTO;

int   currentPhase    = PHASE_RED;
unsigned long phaseStart  = 0;

unsigned long blinkPrev   = 0;
bool          blinkState  = false;

// Антидребезг кнопки
bool          lastButtonState = HIGH;
unsigned long lastDebounce    = 0;
const unsigned long DEBOUNCE_DELAY = 50;

// -------------------------------------------------------

void allOff() {
  digitalWrite(PIN_RED,    LOW);
  digitalWrite(PIN_YELLOW, LOW);
  digitalWrite(PIN_GREEN,  LOW);
}

void setPhase(int phase) {
  allOff();
  switch (phase) {
    case PHASE_RED:
      digitalWrite(PIN_RED, HIGH);
      break;
    case PHASE_RED_YELLOW:
      digitalWrite(PIN_RED,    HIGH);
      digitalWrite(PIN_YELLOW, HIGH);
      break;
    case PHASE_GREEN:
      digitalWrite(PIN_GREEN, HIGH);
      break;
    case PHASE_YELLOW:
      digitalWrite(PIN_YELLOW, HIGH);
      break;
  }
}

// -------------------------------------------------------

void setup() {
  Serial.begin(9600);

  pinMode(PIN_RED,    OUTPUT);
  pinMode(PIN_YELLOW, OUTPUT);
  pinMode(PIN_GREEN,  OUTPUT);
  pinMode(PIN_BUTTON, INPUT_PULLUP);

  // Восстановить режим из EEPROM
  byte saved = EEPROM.read(EEPROM_MODE_ADDR);
  if (saved == MODE_AUTO || saved == MODE_BLINK) {
    currentMode = saved;
    lastMode    = saved;
  } else {
    currentMode = MODE_AUTO;
    lastMode    = MODE_AUTO;
  }

  Serial.print("Режим из EEPROM: ");
  Serial.println(currentMode == MODE_AUTO ? "AUTO" : "BLINK");

  // Начальное состояние
  currentPhase = PHASE_RED;
  phaseStart   = millis();
  setPhase(PHASE_RED);
}

// -------------------------------------------------------

void loop() {
  unsigned long now = millis();

  // --- Обработка кнопки с антидребезгом ---
  bool reading = digitalRead(PIN_BUTTON);
  if (reading != lastButtonState) {
    lastDebounce = now;
  }
  if ((now - lastDebounce) > DEBOUNCE_DELAY) {
    // Фронт нажатия (HIGH → LOW, т.к. INPUT_PULLUP)
    if (reading == LOW && lastButtonState == HIGH) {
      currentMode = (currentMode == MODE_AUTO) ? MODE_BLINK : MODE_AUTO;

      // Сохранить в EEPROM только при смене
      if (currentMode != lastMode) {
        EEPROM.write(EEPROM_MODE_ADDR, currentMode);
        lastMode = currentMode;
        Serial.print("Режим изменён: ");
        Serial.println(currentMode == MODE_AUTO ? "AUTO" : "BLINK");
      }

      // Сбросить фазу при переходе в AUTO
      if (currentMode == MODE_AUTO) {
        currentPhase = PHASE_RED;
        phaseStart   = now;
        setPhase(PHASE_RED);
      } else {
        allOff();
        blinkState = false;
        blinkPrev  = now;
      }
    }
  }
  lastButtonState = reading;

  // --- Логика режимов ---
  if (currentMode == MODE_AUTO) {
    // Переключение фаз по таймеру
    if (now - phaseStart >= phaseDuration[currentPhase]) {
      currentPhase = (currentPhase + 1) % 4;
      phaseStart   = now;
      setPhase(currentPhase);
    }
  } else {
    // Мигание жёлтым
    if (now - blinkPrev >= BLINK_INTERVAL) {
      blinkPrev  = now;
      blinkState = !blinkState;
      allOff();
      if (blinkState) {
        digitalWrite(PIN_YELLOW, HIGH);
      }
    }
  }
}
