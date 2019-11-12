#include <WiFi.h>
#include <M5StickC.h>


extern const unsigned char gImage_logo[];
long loopTime, startTime, wifiscantime, accscantime = 0;
bool led = true;
uint8_t led_count = 12;
int wificount = 0;

int broad_channel=11;
String ssid_preface = "DGHonk-";
String MYID;

bool report_acc = false;
char buf[100];
float accX_f = 0;
float accY_f = 0;
float accZ_f = 0;

float gyroX_f = 0;
float gyroY_f = 0;
float gyroZ_f = 0;

void wifiTest() {
    M5.Lcd.setTextColor(BLACK, WHITE);
    M5.Lcd.setCursor(7, 0, 2);
    M5.Lcd.println("WIFI TEST");
        
    // WiFi.scanNetworks will return the number of networks found
    int n = WiFi.scanNetworks();
    M5.Lcd.setCursor(7, 20, 2);
    M5.Lcd.println("scan done");
  
  if (n == 0) {
      M5.Lcd.setTextColor(RED, WHITE);
    } else {   
      M5.Lcd.setTextColor(GREEN, WHITE);
    }
    M5.Lcd.setCursor(5, 60, 4);
    M5.Lcd.printf("%d AP", n);
}


void imuTest(){
  M5.IMU.getGyroData(&gyroX_f,&gyroY_f,&gyroZ_f);
  M5.IMU.getAccelData(&accX_f,&accY_f,&accZ_f);
  
  M5.Lcd.setTextColor(GREEN, WHITE);
  M5.Lcd.setCursor(20, 1, 1);
  M5.Lcd.println("mg  o/s");
  M5.Lcd.setCursor(0, 10);
  M5.Lcd.printf("x  %.1f  %.1f", gyroX_f, accX_f);
  M5.Lcd.setCursor(0, 20);
  M5.Lcd.printf("y  %.1f  %.1f", gyroY_f, accY_f);
  M5.Lcd.setCursor(0, 30);
  M5.Lcd.printf("z  %.1f  %.1f", gyroZ_f, accZ_f);
}

void rtcTest(){
  M5.Lcd.setTextColor(RED, WHITE);
  M5.Rtc.GetBm8563Time();
  M5.Lcd.setCursor(0, 50, 1);
  M5.Lcd.printf("Data %02d:%02d:%02d\n",M5.Rtc.Hour, M5.Rtc.Minute, M5.Rtc.Second);
}

// For now, information to rename ssid comes from serial
String get_serial_input(){
  String new_string="";
  if (Serial.available()) {
    new_string = Serial.readString();
  }
  return new_string;
}

int scanWiFi(uint8_t scan_channel, bool returnlist=false) {
  bool async = false;
  bool show_hidden = false;
  bool passive = false;
  uint32_t max_ms_per_chan = 500;

  int numberOfNetworks = WiFi.scanNetworksv2(async, show_hidden, passive, max_ms_per_chan, scan_channel);
 
  if (returnlist){
    Serial.print("Number of networks found: "); Serial.println(numberOfNetworks);
    for (int i = 0; i < numberOfNetworks; i++) {
      //num||Network name||Network channel||Network strength||MAC address
      // Serial.print(i+1);
      // Serial.println("||"+WiFi.SSID(i)+"||"+WiFi.channel(i)+"||"+WiFi.RSSI(i)+"||"+WiFi.BSSIDstr(i));
      snprintf(buf,sizeof(buf), "%d||%s||%d||%d||%s", i+1, WiFi.SSID(i)+"||"+WiFi.channel(i)+"||"+WiFi.RSSI(i)+"||"+WiFi.BSSIDstr(i));
      Serial.println(buf);
    }
  }

  return numberOfNetworks;
}

void dispWifiCount(bool newscan = false){
  // WiFi.scanNetworks will return the number of networks found
  if (newscan){
    M5.Lcd.setTextColor(GREEN, WHITE);
    M5.Lcd.setCursor(0, 50, 1);
    M5.Lcd.println("WIFI Scanning");
    digitalWrite(M5_LED, LOW);
    wificount = scanWiFi(11);
  }

  if (wificount == 0) {
    M5.Lcd.setTextColor(RED, WHITE);
    M5.Lcd.setCursor(0, 70, 2);
    M5.Lcd.printf("%d AP", wificount);
  } else {   
    M5.Lcd.setTextColor(BLACK, WHITE);
    M5.Lcd.setCursor(0, 60, 1);
    for (int i = 0; i < wificount; i++) {
      M5.Lcd.printf("%s||%d||%d\n", WiFi.SSID(i), WiFi.channel(i), WiFi.RSSI(i));
    }
  }
}

void detailed_acc(long timer=100){
  // loopTime = millis();
  // if(timer < (loopTime - 500)){
  // }  
  M5.MPU6886.getGyroData(&gyroX_f,&gyroY_f,&gyroZ_f);
  M5.MPU6886.getAccelData(&accX_f,&accY_f,&accZ_f);

  snprintf(buf,sizeof(buf), "%d %.2f %.2f %.2f %.2f %.2f %.2f", millis(), gyroX_f, gyroY_f, gyroZ_f, accX_f, accY_f, accZ_f);
  Serial.println(buf);

}
  
void set_new_ssid(String rec_ssid){
  rec_ssid = ssid_preface+rec_ssid;
  const char *new_ssid=rec_ssid.c_str();
      
  Serial.print("SSID will be changed to:\t");
  Serial.println(new_ssid);

  WiFi.softAP(new_ssid,NULL,broad_channel,0,0);
}

void run_input(){
  String rec_ssid = get_serial_input();
  uint8_t in_length = rec_ssid.length();
  if (in_length > 0) {
    if (rec_ssid.startsWith("1:")){
      if (in_length == 4){
        scanWiFi(rec_ssid.substring(2,5).toInt(), true);
      }
      else{scanWiFi(11, true);}
    }
    else if (rec_ssid.startsWith("2:")){
      Serial.println(MYID);
    }
    else if (rec_ssid.startsWith("3:")){
      if (rec_ssid.startsWith("3:0")){
        Serial.println("Accelorometer report off");
        report_acc = false;
      }
      else if (rec_ssid.startsWith("3:1")){
        Serial.println("Accelorometer report on");
        report_acc = true;
      }
    }
    else {      
      set_new_ssid(rec_ssid);
    }
  }
}

void m5Startup(){
  // put your setup code here, to run once:
  M5.begin();
  Wire.begin(32,33);
  
  //!Logo
  M5.Lcd.fillScreen(WHITE);
  M5.Lcd.drawBitmap(0, 0, 80, 160,(uint16_t *)gImage_logo);
  delay(1000);

  //!Screen
  M5.Lcd.fillScreen(BLUE);
  delay(150);
  M5.Lcd.fillScreen(RED);
  delay(150);
  M5.Lcd.fillScreen(YELLOW);
  delay(150);
  M5.Lcd.fillScreen(ORANGE);
  delay(150);
  M5.Lcd.fillScreen(WHITE);
  delay(150);

  //!Wifi 
  wifiTest();
  delay(1000);
  M5.Lcd.fillScreen(WHITE);

  //!IMU
  M5.IMU.Init();
  Serial.printf("imuType = %d\n",M5.IMU.imuType);

  //!LED
  pinMode(M5_LED, OUTPUT);
  digitalWrite(M5_LED, LOW);
  pinMode(M5_BUTTON_HOME, INPUT);
  pinMode(M5_BUTTON_RST, INPUT);
}

void dghonkStartup(){
    Serial.begin(115200);
    Serial.setTimeout(200);
    delay(100);
    
    Serial.println(); Serial.println();
    set_new_ssid("ESP_STARTUP2");

    MYID = WiFi.macAddress();

    Serial.println("Startup with SSID:\t"+ssid_preface+"ESP_STARTUP2");
}

void setup() {
  WiFi.mode(WIFI_AP_STA);
  m5Startup();
  dghonkStartup();
}

long sleep_count = 0;
void loop() {
  // put your main code here, to run repeatedly:
  loopTime = millis();
  if(startTime < (loopTime - 500)){
    if(M5.Axp.GetWarningLeve()){
      sleep_count++;
      if(sleep_count >= 1){
        M5.Lcd.fillScreen(WHITE);
        M5.Lcd.setCursor(0, 20, 1);
        M5.Lcd.setTextColor(RED, WHITE);
        M5.Lcd.printf("Warning: low battery");
      }
      if(sleep_count >= 10){
        sleep_count = 0;
        M5.Axp.SetSleep();
      }
    }else{
      M5.Lcd.fillScreen(WHITE);
      imuTest();
      // rtcTest();
      dispWifiCount();
    }    
    startTime = loopTime;
  }

  if(wifiscantime < (loopTime - 10000)){
    dispWifiCount(true);
    wifiscantime = loopTime;
  }

  if(digitalRead(M5_BUTTON_RST) == LOW){
    led = !led;
  }
  digitalWrite(M5_LED, led);


  if(digitalRead(M5_BUTTON_HOME) == LOW){
    led_count++;
    if(led_count > 12)
      led_count = 7;
    while(digitalRead(M5_BUTTON_HOME) == LOW);
    M5.Axp.ScreenBreath(led_count);
  }

  run_input();
  if (report_acc)
    detailed_acc();
}
