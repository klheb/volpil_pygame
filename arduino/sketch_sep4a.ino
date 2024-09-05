void setup() {
    Serial.begin(9600);
}

void loop() {
    float voltage1 = analogRead(A0) * (5.0 / 1023.0);  // Convertir la lecture analogique
    float voltage2 = analogRead(A1) * (5.0 / 1023.0);
    Serial.print(voltage1);
    Serial.print(",");
    Serial.println(voltage2);
    delay(100);  // Délai pour éviter d'envoyer trop rapidement
}

