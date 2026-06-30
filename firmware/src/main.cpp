// Pinos de saída (ajuste conforme a sua montagem física)
const int pinoSolenoid = 4; // Conectado à base do TIP122
const int pinoLedRed = 5;   // Conectado ao LED vermelho

void setup() {
  // Inicia a comunicação serial com o PC a 115200 baud rate 
  Serial.begin(115200);
  
  pinMode(pinoSolenoid, OUTPUT);
  pinMode(pinoLedRed, OUTPUT);
  
  // Garante que iniciam desligados
  digitalWrite(pinoSolenoid, LOW);
  digitalWrite(pinoLedRed, LOW);
}

void loop() {
  if (Serial.available() > 0) {
    char comando = Serial.read();
    
    if (comando == '1') {
      // Acesso Liberado: Aciona Solenoide [cite: 624]
      digitalWrite(pinoSolenoid, HIGH);
      delay(3000); // Mantém a porta aberta por 3 segundos
      digitalWrite(pinoSolenoid, LOW);
    } 
    else if (comando == '0') {
      // Acesso Negado: Aciona LED vermelho [cite: 625]
      digitalWrite(pinoLedRed, HIGH);
      delay(3000); // Mantém o LED aceso por 3 segundos
      digitalWrite(pinoLedRed, LOW);
    }
  }
}
#include <Arduino.h>

// Pinos de saída (ajuste conforme a sua montagem física)
const int pinoSolenoid = 4; // Conectado à base do TIP122
const int pinoLedRed = 5;   // Conectado ao LED vermelho

void setup() {
  // Inicia a comunicação serial com o PC a 115200 baud rate 
  Serial.begin(115200);
  
  pinMode(pinoSolenoid, OUTPUT);
  pinMode(pinoLedRed, OUTPUT);
  
  // Garante que iniciam desligados
  digitalWrite(pinoSolenoid, LOW);
  digitalWrite(pinoLedRed, LOW);
}

void loop() {
  if (Serial.available() > 0) {
    char comando = Serial.read();
    
    if (comando == '1') {
      // Acesso Liberado: Aciona Solenoide [cite: 624]
      digitalWrite(pinoSolenoid, HIGH);
      delay(3000); // Mantém a porta aberta por 3 segundos
      digitalWrite(pinoSolenoid, LOW);
    } 
    else if (comando == '0') {
      // Acesso Negado: Aciona LED vermelho [cite: 625]
      digitalWrite(pinoLedRed, HIGH);
      delay(3000); // Mantém o LED aceso por 3 segundos
      digitalWrite(pinoLedRed, LOW);
    }
  }
}