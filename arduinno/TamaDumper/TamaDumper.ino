
/* tama dumper arduino (leonardo) v0.07 by Mr.Blinky */
/* build using Arduino 1.0.5                         */

#include <SPI.h>

#undef  SS     // SS (SPI Slave Select) on Leonardo is  connected to RxLED and not accessible on any of the normal pins
#define SS 13  // re-assign slave select so SPI.begin() initializes the proper pin

#define SPI_RDSR1  0x05
#define SPI_RDSR2  0x35
#define SPI_WRSR   0x01
#define SPI_RDID   0x9F
#define SPI_READ   0x03

#define SPI_WREN   0x06
#define SPI_WRDI   0x04
#define SPI_PROG   0x02

#define SPI_ERSCT  0x20
#define SPI_ER32K  0x52
#define SPI_ER64K  0xD8
#define SPI_ERCHP  0x60

byte blank = 0;              //set when chip erased
unsigned long addr = 0;      //default start address for dump / flash
unsigned long len = 0x40000; //256KB as default size 
char buf[256];

void setup() {
Serial.begin(115200);  
SPI.begin();
SPI.setClockDivider(SPI_CLOCK_DIV4);
//SPI.setBitOrder(MSBFIRST);
//SPI.setDataMode(SPI_MODE0);
//SPI.setClockDivider(SPI_CLOCK_DIV4);
}

void loop() {
  if (Serial.available() > 0) {
    switch (Serial.read()) {
    case 'i': info(); break;
    case 'a': setAddress(); break;
    case 'l': setLength(); break;
    case 'c': chipErase(); break;
    case 'd': dump(); break;
    case 'h': hexDump(); break;
    case 'p': program(); break;
    default : Serial.println("Usage:\n i - Read device info\n a<address> - Set start address\n l<length> - Set length\n d - Binary dump\n h - Hex dump\n prefix hex numbers with '0x'");
    }
  }
}

void setCmd(byte b) {
  digitalWrite(SS,LOW);
  SPI.transfer(b);
}

void endCmd() {
  digitalWrite(SS,HIGH);
}

void printHex(byte b) {
  if (b < 0x10) Serial.print(0);
  Serial.print(b,HEX);
}

void info() {
  setCmd(SPI_RDID);
  Serial.print("Device ID: ");
  printHex(SPI.transfer(0xFF));
  printHex(SPI.transfer(0xFF));
  printHex(SPI.transfer(0xFF));
  endCmd();
  Serial.print("\nStatus: ");
  setCmd(SPI_RDSR2);
  printHex(SPI.transfer(0xFF));
  endCmd();
  setCmd(SPI_RDSR1);
  printHex(SPI.transfer(0xFF));
  endCmd();
  Serial.println();
}

unsigned long getValue() {
  long result;
  String s;
  while (Serial.available() > 0 && s.length() < 10) {
    s += char(Serial.read());
  }
  if (s.length() > 0) {
    result = strtoul(s.c_str(),0,0);
  } else {
    result = 0;
  }
  Serial.println(result,HEX);
  return result;
}

void setAddress() {
  addr = getValue();
}

void setLength() {
  len = getValue();
}

void chipErase() {
  setCmd(SPI_WREN);
  endCmd();
  setCmd(SPI_ERCHP);
  endCmd();
  Serial.println("Erasing chip ...");
  setCmd(SPI_RDSR1);
  while (SPI.transfer(SPI_RDSR1) & 0x01) ;
  Serial.println("Chip Erased");
  endCmd();
  blank = 1; //signal chip is empty
}

void program() {
  unsigned long p = addr;
  unsigned long e = addr + len;
  while (p < e) {
    Serial.readBytes(buf, 256);
    setCmd(SPI_WREN);
    endCmd();
    setCmd(SPI_PROG);
    SPI.transfer((p >> 16) & 0xFF);
    SPI.transfer((p >> 8) & 0xFF);
    SPI.transfer(p & 0xFF);
    for (int i = 0; i < 256; i++) {
      SPI.transfer(buf[i]);
    }
    endCmd();
    setCmd(SPI_RDSR1);
    while (SPI.transfer(0xFF) & 0x01);
    endCmd();
    Serial.println();
    p += 256;
  }
}

void dump() {
  setCmd(SPI_READ);
  SPI.transfer((addr >> 16) & 0xFF);
  SPI.transfer((addr >> 8) & 0xFF);
  SPI.transfer(addr & 0xFF);
  for (unsigned long ul=0; ul < len ; ul++) {
    Serial.write(SPI.transfer(0xFF));
  }
  endCmd();
}

void hexDump() {
  setCmd(SPI_READ);
  SPI.transfer((addr >> 16) & 0xFF);
  SPI.transfer((addr >> 8) & 0xFF);
  SPI.transfer(addr & 0xFF);
  for (long j=0; j < len ; j++) {
    if (j>0 && (j & 0x1F) == 0) Serial.println();
    printHex(SPI.transfer(0xFF));
  }
  Serial.println();
  endCmd();
}


