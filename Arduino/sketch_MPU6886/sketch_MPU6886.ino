#include <M5StickC.h>

bool out_serial = false;
float accX = 0;
float accY = 0;
float accZ = 0;

float gyroX = 0;
float gyroY = 0;
float gyroZ = 0;

float temp = 0;

char buf[70];
void setup() {
  Serial.begin(115200);
  while(!Serial);
  // put your setup code here, to run once:
  M5.begin();
  M5.Lcd.setRotation(1);
  M5.Lcd.fillScreen(BLACK);
  M5.Lcd.setTextSize(1);
  M5.Lcd.setCursor(0, 5);
  M5.Lcd.println("  X       Y       Z");
  M5.MPU6886.Init();

  pinMode(M5_BUTTON_HOME, INPUT);

  Serial.println("gyroX, gyroY, gyroZ, accX, accY, accZ");
}

void loop() {
  // put your main code here, to run repeatedly:
  M5.MPU6886.getGyroData(&gyroX,&gyroY,&gyroZ);
  M5.MPU6886.getAccelData(&accX,&accY,&accZ);
  M5.MPU6886.getTempData(&temp);

  M5.Lcd.setCursor(0, 20);
  M5.Lcd.printf("%.2f   %.2f   %.2f      ", gyroX, gyroY,gyroZ);
  M5.Lcd.setCursor(140, 20);
  M5.Lcd.print("o/s");
  M5.Lcd.setCursor(0, 35);
  M5.Lcd.printf("%.2f   %.2f   %.2f      ",accX, accY, accZ);
  M5.Lcd.setCursor(140, 35);
  M5.Lcd.print("mg");
  M5.Lcd.setCursor(0, 50);
  M5.Lcd.printf("Temperature : %.2f C", temp);

  if (digitalRead(M5_BUTTON_HOME) == LOW){
    out_serial = !out_serial;

    if (out_serial == false){
      M5.Lcd.fillScreen(BLACK);
      M5.Lcd.setCursor(0, 5);
      M5.Lcd.println("  X       Y       Z");
    }
    while(digitalRead(M5_BUTTON_HOME) == LOW);
  }

  if (out_serial){
    M5.Lcd.setCursor(130, 65);
    M5.Lcd.printf("SER<<");
    snprintf(buf,sizeof(buf), "%d %.2f %.2f %.2f %.2f %.2f %.2f", millis(), gyroX, gyroY, gyroZ, accX, accY, accZ);
    Serial.println(buf);
  }
  delay(100);
  
}
