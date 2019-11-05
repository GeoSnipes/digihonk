#include <ESP8266WiFi.h>

extern "C" {
  #include "user_interface.h"
}

uint8_t channel;
uint8_t beaconMAC[6];
String ssid_preface = "DGHonk-";
String ssid_end = "---";
String old_ssid = "Start";

//Construct beacon frame
uint16_t beaconPacket(uint8_t* output, uint8_t channel, uint8_t* mac, String& ssid){
    //MAC HEADER
    *(output++) = 0x80;  *(output++) = 0x00;  //Frame Control
    *(output++) = 0x00;  *(output++) = 0x00;  //Duration
    *(output++) = 0xFF; *(output++) = 0xFF; *(output++) = 0xFF;     /*4*/   //DA- Broadcast
    *(output++) = 0xFF; *(output++) = 0xFF; *(output++) = 0xFF;     
    for (uint8_t i=0; i<6; i++) *(output++) = mac[i];               /*10*/  //Source address
    for (uint8_t i=0; i<6; i++) *(output++) = mac[i];               /*16*/  //BSS ID
    *(output++) = 0xC0; *(output++) = 0x6C;                         /*22*/  //Seq-ctl

    //FRAME BODY
    *(output++) = 0x83; *(output++) = 0x51; *(output++) = 0xF7; *(output++) = 0x8F; /*24*/ // timestamp
    *(output++) = 0x0F; *(output++) = 0x00; *(output++) = 0x00; *(output++) = 0x00;
    *(output++) = 0x64; *(output++) = 0x00;                         /*32*/  //Beacon interval
    *(output++) = 0x01; *(output++) = 0x04;                         /*34*/  //Capability info  0x01 0x04
    
    //CONSTRUCT SSID INFORMATION
    uint16_t ssid_amount = ssid.length();
    *(output++) = 0;                                                /*36*/  // 0 = SSID
    *(output++) = ssid_amount;                                      /*37*/ //Length of SSID
    for (uint16_t i=0; i < ssid_amount; i++){
        *(output++) = ssid[i];
    }

    *(output++) = 0x01; *(output++) = 0x08;                     // 1 = supported rates, length = 8
    *(output++) = 0x82; *(output++) = 0x84; *(output++) = 0x8B; *(output++) = 0x96;
    *(output++) = 0x24; *(output++) = 0x30; *(output++) = 0x48; *(output++) = 0x6C;
    
    *(output++) = 0x03; *(output++) = 0x01; *(output++) = channel; // 3 = DSPS/channel, length = 1

    uint16_t returnValue = 51 +ssid_amount;
    return returnValue;
}

// For now, information to rename ssid comes from serial
String get_ssid(){
  String new_string="";
  if (Serial.available()) {
    new_string = Serial.readStringUntil('\n');
  }
  return new_string;
}

void send_beacon(String ssid){
    uint8_t  beaconData[128];
    uint16_t packetSize = beaconPacket(beaconData, channel, beaconMAC, ssid);
    
    wifi_send_pkt_freedom(beaconData, packetSize, 0);
}

void setup() {
    Serial.begin(115200);
    delay(500);
    wifi_set_opmode(STATION_MODE);
    wifi_promiscuous_enable(1); 

    //On first run, pick a random channel to use
    channel = random(1,12);
    wifi_set_channel(channel);
    
    //On first run, create random source address
    beaconMAC[0] = random(256);
    beaconMAC[1] = random(256);
    beaconMAC[2] = random(256);
    beaconMAC[3] = random(256);
    beaconMAC[4] = random(256);
    beaconMAC[5] = random(256);

    Serial.println(); Serial.println();
    Serial.print("Using channel:\t"); Serial.println(channel);
    Serial.print("Source address:\t");
    for(int i=0; i<sizeof(beaconMAC); i++){
      Serial.print(beaconMAC[i]); Serial.print(".");
    }
    Serial.println(); Serial.println();
}

void loop() {
  String new_ssid = get_ssid();

  
  if (new_ssid.length() >0) {
    Serial.print("SSID will be changed to:\t");
    Serial.println(ssid_preface+new_ssid);
    
    send_beacon(ssid_preface+new_ssid+ssid_end);
    old_ssid=new_ssid;
    new_ssid="";
  }
  else{
    send_beacon(ssid_preface+old_ssid);
   }
}
