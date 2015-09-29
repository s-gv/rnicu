/*
This program samples analog signals at 400 Hz and sends the sampled data via UART

Copyright (C) 2014  Sagar G V (sagar.writeme@gmail.com)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

#include "DueTimer.h"


int led = 13; // orange LED
int analogInPin = 8; // analog Pin A8
int analogOutPin = DAC0; // analog Pin DAC

int val, i;

int amp = 0;
int phase = 0;
extern int sine_arr[10][20];

void dumpval(unsigned int val) {
    unsigned char lsb = val & 0x3F; // lower 6 bits
    unsigned char msb = (val >> 6) & 0x3F; // upper 6 bits
    msb |= 0x40; // msb encoding
    Serial1.write(lsb);
    Serial1.write(msb);
}

void debugdump(unsigned int val) {
    unsigned char lsb = val & 0x3F; // lower 6 bits
    lsb |= 0x80; // lsb encoding
    unsigned char msb = (val >> 6) & 0x3F; // upper 6 bits
    msb |= 0xC0; // msb encoding
    Serial1.write(lsb);
    Serial1.write(msb);
}

void timerHandler() {
  int temp;
  val = analogRead(analogInPin);
  dumpval(val);
  /* // The following is a failed experiment.
  // saw tooth wave
  int key = Serial1.read();
  if(key == '1') {
    if(amp < 9)
      amp++;
  }
  if(key == '2') {
    if(amp > 0)
      amp--;
  }
  if(key == '3') {
    i++; // increase phase
  }
  if(key == '4') {
    if(i==0)
      i = 19;
    else
      i--;
  }
  i++;
  i = i % 20;
  temp = sine_arr[amp][i];
  */
  temp = 2048;
  analogWrite(analogOutPin, temp);
}

void setup() {
  Serial1.begin(115200);
  pinMode(led, OUTPUT); // initialize the digital pin as an output.
  Timer.getAvailable().attachInterrupt(timerHandler).start(2500); // call timerHandler once in 2500 us
  analogReadResolution(12);
  analogWriteResolution(12);
  analogWrite(analogOutPin, 2048);
  analogWrite(DAC1, 2048);
  
  debugdump(4095); // reset plot on the visualizer
}

void loop() {
}
