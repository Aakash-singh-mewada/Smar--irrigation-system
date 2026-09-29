/*
  Smart Automatic Irrigation - Arduino Uno implementation
  Same logic as irrigation/controller.py (hysteresis + safety limits).

  Wiring:
    Soil moisture sensor (capacitive) AOUT -> A0, VCC -> 5V, GND -> GND
    Relay module IN -> D7, VCC -> 5V, GND -> GND
    Water pump (through relay NO/COM) powered from its own supply
*/
const int SENSOR_PIN = A0;
const int RELAY_PIN  = 7;

// Calibrate: raw value in dry air and in a glass of water
const int RAW_DRY = 850;
const int RAW_WET = 400;

const float MOISTURE_LOW  = 35.0;            // % -> start pump
const float MOISTURE_HIGH = 65.0;            // % -> stop pump
const unsigned long MAX_RUN_MS = 20UL * 60UL * 1000UL;   // 20 min safety
const unsigned long MIN_GAP_MS = 60UL * 60UL * 1000UL;   // 60 min cooldown

bool pumpOn = false;
unsigned long startedAt = 0, stoppedAt = 0;
bool hasStopped = false;

float readMoisturePercent() {
  long sum = 0;
  for (int i = 0; i < 10; i++) { sum += analogRead(SENSOR_PIN); delay(10); }
  float raw = sum / 10.0;
  float pct = (RAW_DRY - raw) * 100.0 / (RAW_DRY - RAW_WET);
  return constrain(pct, 0.0, 100.0);
}

void setPump(bool on) {
  pumpOn = on;
  digitalWrite(RELAY_PIN, on ? LOW : HIGH);   // most relay boards are active-LOW
  if (on) startedAt = millis(); else { stoppedAt = millis(); hasStopped = true; }
}

void setup() {
  Serial.begin(9600);
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, HIGH);              // pump OFF at boot
}

void loop() {
  float m = readMoisturePercent();
  unsigned long now = millis();

  if (pumpOn) {
    if (m >= MOISTURE_HIGH || now - startedAt >= MAX_RUN_MS) setPump(false);
  } else if (m <= MOISTURE_LOW && (!hasStopped || now - stoppedAt >= MIN_GAP_MS)) {
    setPump(true);
  }

  Serial.print("moisture="); Serial.print(m);
  Serial.print("% pump="); Serial.println(pumpOn ? "ON" : "OFF");
  delay(5000);
}
