
/* 
 Programme de test pour servomoteur de positionnement angulaire 
 Traduction en français, ajout de variables
 Code original de BARRAGAN <http://barraganstudio.com>
 et Scott Fitzgerald http://www.arduino.cc/en/Tutorial/Sweep
 
 www.projetsdiy.fr - 19/02/2016
 public domain
*/

/*Allow the controll of a simple arm with an elbow and a hand. It can be controlled as follow :
  - a number between 0 and 180 is understand as the new angle position the elbow should take
  - 181 is hand opening
  - 182 is hand closing
Note that our hand only consited in a static thumb and an other finger mooved by a motor*/

#include <Servo.h>

Servo coude;  // création de l'objet myservo 
Servo poignee;

int incomingByte = 0; // for incoming serial data

int pin_coude = 13;       // Pin sur lequel est branché le coude
int pin_main = 7;

float pos_main = 135;

void setup() {
  Serial.begin(9600);                       
  while(!Serial){;} 
  coude.attach(pin_coude);  // attache le servo au pin spécifié sur l'objet myservo
  coude.write(90);
  poignee.attach(pin_main);
  poignee.write(pos_main);
}



void loop() 
{
  if(Serial.available() > 0)
  {
    incomingByte = Serial.read();
    //Serial.println(incomingByte);
    if(incomingByte < 181)
    {
      coude.write(incomingByte);
    }
    else if(incomingByte == 181) //ouverture
    {
      while(pos_main > 75)
      {
        pos_main -= 0.4;
        poignee.write(pos_main);
        delay(5);
      }
    }
    else if(incomingByte == 182) //fermeture
    {
      while(pos_main < 200)
      {
        pos_main += 0.4;
        poignee.write(pos_main);
        delay(5);
      }
    }
  }  
}









