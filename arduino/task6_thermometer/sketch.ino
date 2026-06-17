#include <EEPROM.h>

#define PIN_BLUE   5
#define PIN_GREEN  6
#define PIN_YELLOW 7
#define PIN_RED    8

const float BETA = 3950;

float readTemp() {
  int raw = analogRead(A0);
  return 1.0 / (log(1.0 / (1023.0 / raw - 1)) / BETA + 1.0 / 298.15) - 273.15;
}

float readFromEEPROM() {
  float t;
  EEPROM.get(0, t);
  return t;
}

void setup() {
  Serial.begin(9600);
  for (int p = 5; p <= 8; p++) pinMode(p, OUTPUT);
  Serial.print("Из EEPROM: ");
  Serial.print(readFromEEPROM(), 1);
  Serial.println(" C");
}

void loop() {
  float t = readFromEEPROM();

  digitalWrite(PIN_BLUE,   t < 20);
  digitalWrite(PIN_GREEN,  t >= 20 && t < 30);
  digitalWrite(PIN_YELLOW, t >= 30 && t < 40);
  digitalWrite(PIN_RED,    t >= 40);

  Serial.print(t, 1);
  Serial.println(" C");

  EEPROM.put(0, readTemp());

  delay(1000);
}
