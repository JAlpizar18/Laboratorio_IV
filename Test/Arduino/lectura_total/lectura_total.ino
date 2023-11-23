bool enablePin1 = true;
bool enablePin2 = true;

const int pin1 = 0; // Pin analógico 0
const int pin2 = 1; // Pin analógico 1

const int analogPinPos = 3; // Pin analógico donde está conectado el punto positivo del puente
const int analogPinNeg = 4; // Pin analógico donde está conectado el punto negativo del puente

const int referenceVoltage1 = 0;
const int referenceVoltage2 = 0;
const int temperatureIncrement = 8;
const int numSamples = 2000;

int muxPins[3] = {2, 3, 4}; // Pines para controlar el multiplexor
int muxPins2[3] = {5, 6, 7};

int Temp1 = 0;
int Temp2 = 0;
int Ta = 0;
volatile bool newDataFlag = false;  // Bandera para indicar nuevos datos desde Python


int canal_seleccionado = 0;
int escala_seleccionada = 0;
bool canal1_seleccionado = false;
bool canal2_seleccionado = false;





void setup() {
  Serial.begin(9600);

  pinMode(pin1, INPUT);
  pinMode(pin2, INPUT);

  pinMode(analogPinPos, INPUT);
  pinMode(analogPinNeg, INPUT);

  // Configura los pines del multiplexor como salidas
  for (int i = 0; i < 3; i++) {
    pinMode(muxPins[i], OUTPUT);
    pinMode(muxPins2[i], OUTPUT);
  }

  Serial.println("init ok");
}

void recibirDatosDesdePython() {
  if (Serial.available() > 0) {
    String mensajeRecibido = Serial.readStringUntil('\n');
   
    if (mensajeRecibido.length() > 0) {
      // Dividir el mensaje en partes usando comas como delimitador
      String partes[4];
      int posComa = -1;

      for (int i = 0; i < 4; i++) {
        int nuevaPosComa = mensajeRecibido.indexOf(',', posComa + 1);

        if (nuevaPosComa != -1) {
          partes[i] = mensajeRecibido.substring(posComa + 1, nuevaPosComa);
          partes[i].trim();
          posComa = nuevaPosComa;
        } else {
          // Si no se encuentra una coma, se detiene el bucle
          break;
        }
      }
     
      escala_seleccionada = atoi(partes[0].c_str());
      canal_seleccionado = atoi(partes[1].c_str());
      canal1_seleccionado = partes[2] == "True";
      canal2_seleccionado = partes[3] == "True";

      
        
      newDataFlag = true;
    }
  }
}

void procesarDatos() {
  // Actualizar las variables en el Arduino con los valores recibidos
  if (canal_seleccionado == 1) {
     controlarMultiplexor(1, escala_seleccionada);

  } else if (canal_seleccionado == 2) {
    controlarMultiplexor(2, escala_seleccionada);
  }
  enablePin1 = canal1_seleccionado;
  enablePin2 = canal2_seleccionado;

}

void controlarMultiplexor(int muxNumber, int value) {
  if (value >= 0 && value <= 5) {
    int *muxPinsToControl = (muxNumber == 1) ? muxPins : muxPins2;
    for (int i = 0; i < 3; i++) {
      digitalWrite(muxPinsToControl[i], bitRead(value, i));
    }
  } else {
    //Serial.print("Valor del multiplexor ");
    //Serial.print(muxNumber);
    //Serial.println(" no válido.");
  }
}

void leerDatosDesdePython(){
  Serial.print(Temp1);
  Serial.print(",");
  Serial.print(Temp2);
  Serial.print(",");
  Ta=23;
  Serial.println(Ta);
}



void lecturaAnalogico(int pin1, int pin2) {
  unsigned long startTime1 = micros(); // Tiempo de inicio para pin1
  unsigned long startTime2 = micros(); // Tiempo de inicio para pin2

  int analogVoltage1;
  int analogVoltage2;

  for (int i = 0; i < numSamples; i++) {
    if (enablePin1) {
      while (micros() - startTime1 < 500) {
        // Espera hasta que hayan transcurrido 500 microsegundos
      }
      int analog1rawvalue = analogRead(pin1);
      analogVoltage1 = map(analog1rawvalue, 0, 1023, 0, 5000); // Mapear a mV
      // Puedes hacer algo con analogVoltage1 si es necesario
      startTime1 = micros(); // Establecer el próximo tiempo de inicio para pin1
  }

    if (enablePin2) {
      while (micros() - startTime2 < 500) {
        // Espera hasta que hayan transcurrido 500 microsegundos
      }
      int analog2rawvalue = analogRead(pin2);
      analogVoltage2 = map(analog2rawvalue, 0, 1023, 0, 5000); // Mapear a mV
      // Puedes hacer algo con analogVoltage2 si es necesario
      startTime2 = micros(); // Establecer el próximo tiempo de inicio para pin2
    }

    int Temperature1 = int((analogVoltage1 - referenceVoltage1) / temperatureIncrement);
    int Temperature2 = int((analogVoltage2 - referenceVoltage2) / temperatureIncrement);

    Temp1 = Ta + Temperature1;
    Temp2 = Ta + Temperature2;
  leerDatosDesdePython();
  
  }
}

// Función para calcular y mostrar la temperatura
void calcularTemperaturaAmbiente() {
  // Leer valores analógicos de los pines del puente
  int lecturaPositiva = analogRead(analogPinPos);
  int lecturaNegativa = analogRead(analogPinNeg);

  int lecturaVoltagePositivo = map(lecturaPositiva, 0, 1023, 0, 5000);
  int lecturaVoltagenegativo =map(lecturaNegativa, 0, 1023, 0, 5000);

  // Calcular la diferencia de voltaje en milivoltios
  int diferenciaVoltaje = (lecturaVoltagePositivo - lecturaVoltagenegativo);

  float resistance = (diferenciaVoltaje * 2000.0) / (10.0 - diferenciaVoltaje);
  float inv_T = 1.0 / 296.15 + (1.0 / 3950.0) * log(resistance / 2000.0);
  float tempK = 1.0 / inv_T;
  Ta = int(tempK - 273.15);

  // Imprimir el resultado
  Serial.print("Diferencia de Voltaje (mV): ");
  Serial.print(diferenciaVoltaje);
  Serial.print("   Temperatura (°C): ");
  Serial.println(Ta);
 
}
void loop() {
  calcularTemperaturaAmbiente();
  lecturaAnalogico(pin1,pin2);
  recibirDatosDesdePython(); 
    if (newDataFlag) {
      procesarDatos();  // Procesar los nuevos datos
      newDataFlag = false;  // Reiniciar la bandera
    }
 
}


