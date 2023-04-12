uint16_t delta = 18000;


void setup() {
    Serial.begin(115200);
    light_dimmer();
}

void loop() {
    while (!Serial.available());
    if (Serial.read() == '.') delta -= 256;
    else delta += 256;
    Serial.println(delta);
}


void light_dimmer() {
    cli();
    DDRD |= (1 << 6);
    TCCR1A = 0b00;      // обычный режим
    TCCR1B = 0b010;     // прескелер на 8
    OCR1A = 0;          // значение A
    TIMSK1 = 0b010;     // разрешаем А
    EIMSK |= (1 << 0);  // включаем int0
    EICRA |= 0b11;      // на rising
    sei();
}

ISR(INT0_vect) {
    PORTD &= ~(1 << 6);
    OCR1A = delta;      // значение A
    TIFR1 |= (1 << 1);  // сброс флага A
    TCNT1 = 0;          // сброс счетчика
}

ISR(TIMER1_COMPA_vect) {
    PORTD |= (1 << 6);
}
