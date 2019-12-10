#include <WiFi.h>
#include <M5StickC.h>


extern const unsigned char gImage_logo[];
long loopTime, startTime, wifiscantime, accscantime = 0;
bool led = true; 
uint8_t led_count = 12;
int wificount = 0;

int broad_channel=11;
String ssid_preface = "DGHonk-";
String dgh_last_command = "";
bool dghonk_mode = false;
bool dgh_go = false;

long sleep_count = 0;

char buf[1000];

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


// For now, information to rename ssid comes from serial
String get_serial_input(){
  String new_string="";
  if (Serial.available()) {
    // new_string = Serial.readString());
    new_string = Serial.readStringUntil('\r\n');
    dgh_last_command = new_string;
  }
  return new_string;
}

int scanWiFi(uint8_t scan_channel, bool returnlist=false) {
  bool async = false;
  bool show_hidden = false;
  bool passive = false;
  uint32_t max_ms_per_chan = 400;

  int numberOfNetworks = WiFi.scanNetworksv2(async, show_hidden, passive, max_ms_per_chan, scan_channel);
 
  if (returnlist){
    Serial.print("Number of networks found: "); Serial.println(numberOfNetworks);
    for (int i = 0; i < numberOfNetworks; i++) {
      //num||Network name||Network channel||Network strength||MAC address
       Serial.print(i+1);
       Serial.println("||"+WiFi.SSID(i)+"||"+WiFi.channel(i)+"||"+WiFi.RSSI(i)+"||"+WiFi.BSSIDstr(i));
      //snprintf(buf,sizeof(buf), "%d||%s||%d||%d||%s", i+1, WiFi.SSID(i),WiFi.channel(i),WiFi.RSSI(i),WiFi.BSSIDstr(i));
      //Serial.println(buf);
    }
  }

  return numberOfNetworks;
}

void dispWifiCount(bool newscan = false){
  // WiFi.scanNetworks will return the number of networks found
  if (newscan){
    M5.Lcd.setTextColor(GREEN, WHITE);
    M5.Lcd.setCursor(4, 50, 1);
    M5.Lcd.println("WIFI Scanning");
    digitalWrite(M5_LED, LOW);
    wificount = scanWiFi(11);
    digitalWrite(M5_LED, HIGH);
  }

  if (wificount == 0) {
    M5.Lcd.setTextColor(RED, WHITE);
    M5.Lcd.setCursor(4, 30, 2);
    M5.Lcd.printf("%d AP", wificount);
  } else {   
    M5.Lcd.setTextColor(BLACK);
    M5.Lcd.setCursor(4, 40, 1);
    for (int i = 0; i < wificount; i++) {
      M5.Lcd.print(WiFi.SSID(i)); M5.Lcd.print("||");
      M5.Lcd.print(WiFi.channel(i)); M5.Lcd.print("||");
      M5.Lcd.print(WiFi.RSSI(i)); M5.Lcd.println();
    }
  }
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
      Serial.println(WiFi.macAddress());
    }
    else if (rec_ssid.startsWith("dgh:0")){
      dghonk_mode = false;
      dgh_go = false;
    }
    else if (rec_ssid.startsWith("dgh:1")){
      dghonk_mode = true;
      M5.Lcd.fillScreen(RED);
    }
    else if (rec_ssid.startsWith("dgh:2")){
      dgh_go = true;
      // for measuring time
      Serial.println("dgh:0");
      dghonk_mode = false;
      dgh_go = false;
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
    Serial.setTimeout(200);
    delay(100);
    
    Serial.println(); Serial.println();
    // set_new_ssid("ESP_STARTUP2");
    set_new_ssid("---");

    Serial.println("Startup with SSID:\t"+ssid_preface+"---");
}

void setup() {
  WiFi.mode(WIFI_AP_STA);
  m5Startup();
  dghonkStartup();
  M5.Lcd.setRotation(1);
}

void loop() {
  loopTime = millis();
  if(startTime < (loopTime - 500)){
    if(M5.Axp.GetWarningLeve()){
      sleep_count++;
      if(sleep_count >= 1){
        M5.Lcd.fillScreen(WHITE);
        M5.Lcd.setCursor(4, 20, 1);
        M5.Lcd.setTextColor(RED, WHITE);
        M5.Lcd.printf("Warning: low battery");
      }
      if(sleep_count >= 10){
        sleep_count = 0;
        M5.Axp.SetSleep();
      }
    }else{
      if (dghonk_mode){
        if (dgh_go){
          M5.Lcd.fillScreen(GREEN);
        }
        else{
          M5.Lcd.fillScreen(RED);
        }
      }
      else{
        M5.Lcd.fillScreen(WHITE);
      }
      
      //imuTest();
      dispWifiCount();
    }    
    startTime = loopTime;
  }
  M5.Lcd.setTextColor(BLACK);
  M5.Lcd.setCursor(4, 5, 1);
  M5.Lcd.println(dgh_last_command.length());
  M5.Lcd.println(dgh_last_command);

  if(wifiscantime < (loopTime - 30000)){
    dispWifiCount(true);
    wifiscantime = loopTime;
  }

  if (dghonk_mode != true){
    if(digitalRead(M5_BUTTON_HOME) == LOW){
      Serial.println("dgh:1");
      dghonk_mode = true;
      M5.Lcd.fillScreen(RED);
      while(digitalRead(M5_BUTTON_HOME) == LOW);
    }
  }
  else {
    if (dgh_go == true){
      if(digitalRead(M5_BUTTON_HOME) == LOW){
        Serial.println("dgh:0");
        dghonk_mode = false;
        dgh_go = false;
        while(digitalRead(M5_BUTTON_HOME) == LOW);
      }
    }
  }
  run_input();
}
