#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>
#include <ArduinoBLE.h>

Adafruit_BNO055 bno = Adafruit_BNO055(55);

// const char* deviceServiceUuid = "180C";
// const char* deviceServiceResponseCharacteristicUuid = "2A56";

BLEService IMUService("082b91ae-e83c-11e8-9f32-f2801f1b9fd1");

BLEFloatCharacteristic accelX("082b9438-e83c-11e8-9f32-f2801f1b9fd1", BLERead|BLENotify);
BLEFloatCharacteristic accelY("082b9622-e83c-11e8-9f32-f2801f1b9fd1", BLERead|BLENotify);
BLEFloatCharacteristic accelZ("082b976c-e83c-11e8-9f32-f2801f1b9fd1", BLERead|BLENotify);

void setup() {
  // put your setup code here, to run once:

  Serial.begin(9600);
  
  Serial.println("Orientation Sensor with bluetooth stream Test");
  Serial.println("");

  if (!bno.begin())
  {
    Serial.println("No BNO055 detected");
    while(1);
  }

  if (!BLE.begin())
  {
    Serial.println("Starting BLE failed!");
    while(1);
  }

  IMUService.addCharacteristic(accelX);
  IMUService.addCharacteristic(accelY);
  IMUService.addCharacteristic(accelZ);


  BLE.setLocalName("IMU_BLE");
  BLE.setAdvertisedService(IMUService);
  BLE.addService(IMUService);

  BLE.advertise();
  Serial.println("BLE is active");

  delay(1000);

  bno.setExtCrystalUse(true);

}

void loop() {
  // put your main code here, to run repeatedly:

  BLEDevice central = BLE.central();
  imu::Vector<3> acc = bno.getVector(Adafruit_BNO055::VECTOR_ACCELEROMETER);

  if (central)
  {
    
    Serial.print("Connected to central: ");
    Serial.println(central.address());

    while (central.connected())
    {

      imu::Vector<3> acc = bno.getVector(Adafruit_BNO055::VECTOR_ACCELEROMETER);

      // Serial.print("X: ");
      // Serial.print(acc.x());

      // Serial.print(" Y: ");
      // Serial.print(acc.y());

      // Serial.print(" Z: ");
      // Serial.print(acc.z());
      // Serial.println("");

      float xReading = acc.x();
      float yReading = acc.y();
      float zReading = acc.z();

      accelX.writeValue(xReading);
      accelY.writeValue(yReading);
      accelZ.writeValue(zReading);

      // Calculating incline
      float pitch;
      pitch = (atan2(xReading, sqrt(yReading*yReading + zReading*zReading))* 180)/M_PI;


      Serial.println(pitch);

      delay(50);

    }
  }

}
