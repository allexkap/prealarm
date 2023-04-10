#define DELTA 9000      // us
#define EXTRA 900000    // ms


#include <SoftwareSerial.h>
SoftwareSerial BTSerial(4, 5);

volatile uint64_t crossing = 0;
uint64_t delta = -1;

uint64_t timestamp = 0;
volatile uint64_t step = 0;
volatile bool state = 0;


void setup() {
    BTSerial.begin(9600);

    DDRD |= (1 << 6);   // light dimmer
    DDRD |= (1 << 7);   // button GND
    DDRB |= (1 << 1);   // button OUT
    PORTB |= (1 << 1);  // button VCC

    attachInterrupt(0, trigger, RISING);
    attachInterrupt(1,   abort, RISING);
}

void loop() {
    cli();
    if (micros() - crossing >= delta) PORTD |= (1 << 6);
    sei();

    if (millis() - timestamp >= step) {
        timestamp = millis();
        if (state) {
            if (!--delta) {
                step = EXTRA;
                state = 0;
            }
        }
        else {
            while (!BTSerial.available());
            BTSerial.write(step = BTSerial.read());
            delta = DELTA;
            state = 1;
        }
    }
}

void trigger() {
    PORTD &= ~(1 << 6);
    crossing = micros();
}

void abort() {
    state = step = 0;
}
