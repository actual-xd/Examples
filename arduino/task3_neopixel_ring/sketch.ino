#include <Adafruit_NeoPixel.h>
#include <EEPROM.h>


#define LED_PIN 6
#define LED_COUNT 16  // leds in ring
#define BRIGHTNESS 255 // 0 - 255


#define SWITCH_PIN 2


#define EEPROM_STATE_ADDR 0
#define STATE_LEFT 0   // Против часовой стрелки
#define STATE_RIGHT 1  // По часовой стрелке

Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);


int currentPosition = 0;
unsigned long previousMillis = 0;
const long animationInterval = 150;


int currentState = STATE_LEFT;
int lastState = STATE_LEFT;

void setup() {
  pinMode(SWITCH_PIN, INPUT_PULLUP);

  strip.begin();
  strip.setBrightness(BRIGHTNESS);
  strip.show();


  lastState = EEPROM.read(EEPROM_STATE_ADDR);
  if (lastState > STATE_RIGHT) {
    lastState = STATE_LEFT;
  }


}

void loop() {

  bool switchPressed = digitalRead(SWITCH_PIN) == LOW;


  if (switchPressed) {
    currentState = STATE_RIGHT; // Вправо - по часовой стрелке
  } else {
    currentState = STATE_LEFT;  // Влево - против часовой стрелки
  }

  // Сохранение состояния в EEPROM при изменении
  if (currentState != lastState) {
    EEPROM.write(EEPROM_STATE_ADDR, currentState);

    lastState = currentState;
  }

  // Анимация вращения
  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= animationInterval) {
    previousMillis = currentMillis;

    if (currentState == STATE_LEFT) {
      // Вращение против часовой стрелки
      currentPosition--;
      if (currentPosition < 0) {
        currentPosition = LED_COUNT - 1;
      }
    } else {
      // Вращение по часовой стрелке
      currentPosition++;
      if (currentPosition >= LED_COUNT) {
        currentPosition = 0;
      }
    }

    updateLEDs();
  }
}

void updateLEDs() {
  strip.clear();
  
  // Один яркий светодиод без шлейфа
  if (currentState == STATE_LEFT) {
    // Синий для вращения против часовой
    strip.setPixelColor(currentPosition, strip.Color(0, 0, 255));
  } else {
    // Красный для вращения по часовой
    strip.setPixelColor(currentPosition, strip.Color(255, 0, 0));
  }

  strip.show();
}
