#define DELTA 10000
#define EXTRA 5000
#define STEP  30 * 60*1000/DELTA


#include <SoftwareSerial.h>

volatile uint64_t crossing = 0;
uint64_t delta = DELTA;

uint64_t timestamp = 0, step = STEP, extra = EXTRA;
bool state = 0;

SoftwareSerial BTSerial(4, 5);


void setup() {
    BTSerial.begin(9600);
    DDRD |= (1 << 6);
    attachInterrupt(0, trigger, RISING);
}

void loop() {
    cli();
    if (micros() - crossing >= delta) PORTD |= (1 << 6);
    sei();

    if (millis() - timestamp >= step) {
        timestamp = millis();
        if (state) {
            if (!--delta) state = 0;
        }
        else {
            if (!--extra) {
                state = 1;
                delta = DELTA;
                extra = EXTRA;
                wait();
            }
        }
    }
}

void trigger() {
    PORTD &= ~(1 << 6);
    crossing = micros();
}

void wait() {
    while (!BTSerial.available());
    step = BTSerial.parseInt();
}
