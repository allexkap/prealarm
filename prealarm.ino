volatile uint8_t value = 150;


void setup() {
    light_dimmer();
}

void loop() {
    if (!--value) value -= 110;
    delay(100);
}


void light_dimmer() {
    cli();
    DDRD |= (1 << 6);
    TCCR2A = 0b0;
    TCCR2B = 0b111;
    attachInterrupt(0, zero_cross, RISING);
    sei();
}

void zero_cross() {
    PORTD &= ~(1 << 6);
    GTCCR |= 2;
    TCNT2 = 0;
    TIMSK2 = 0b10;
    OCR2A = value;
}

ISR(TIMER2_COMPA_vect) {
    PORTD |= (1 << 6);
    TIMSK2 = 0;
}
