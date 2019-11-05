#include <WiFi.h>

int broad_channel=11;
String ssid_preface = "DGHonk-";
String MYID;

// For now, information to rename ssid comes from serial
String get_ssid(){
  String new_string="";
  if (Serial.available()) {
    new_string = Serial.readString();
  }
  return new_string;
}

void scanNetworks(uint8_t scan_channel=0) {
  bool async = false;
  bool show_hidden = false;
  bool passive = false;
  uint32_t max_ms_per_chan = 500;

  int numberOfNetworks = WiFi.scanNetworks(async, show_hidden, passive, max_ms_per_chan, scan_channel);
 
  Serial.print("Number of networks found: ");
  Serial.println(numberOfNetworks);
 
  for (int i = 0; i < numberOfNetworks; i++) {
    //Network name||Network channel||Network strength||MAC address
    Serial.print(i+1);
    Serial.println("||"+WiFi.SSID(i)+"||"+WiFi.channel(i)+"||"+WiFi.RSSI(i)+"||"+WiFi.BSSIDstr(i));
  }
}

void new_ssid(String rec_ssid){
  rec_ssid = ssid_preface+rec_ssid;
  const char *new_ssid=rec_ssid.c_str();
      
  Serial.print("SSID will be changed to:\t");
  Serial.println(new_ssid);

  WiFi.softAP(new_ssid,NULL,broad_channel,0,0);
}

void setup() {
    Serial.begin(115200);
    Serial.setTimeout(200);
    delay(100);
    
    Serial.println(); Serial.println();
    new_ssid("ESP_STARTUP");

    MYID = WiFi.macAddress();

    Serial.println("Startup with SSID:\t"+ssid_preface+"ESP_STARTUP");
}

void loop() {
  String rec_ssid = get_ssid();
  uint8_t in_length = rec_ssid.length();
  if (in_length > 0) {
    if (rec_ssid.startsWith("1:")){
      if (in_length == 4){
        scanNetworks(rec_ssid.substring(2,4).toInt());
      }
      else{scanNetworks(11);}
    }
    else if (rec_ssid.startsWith("2:")){
      Serial.println(MYID);
    }
    else {      
      new_ssid(rec_ssid);
    }
  }
}
