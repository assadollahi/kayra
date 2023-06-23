i2cListener.py plus i2cSlave.py 
software that listens at the i2c connection when the controller is in i2c slave mode.
for this, the i2cSlave library is used, cf https://python-academia.com/en/raspberry-pi-pico-slave/
currently, this is only for debuging the ESP32 Cam to Servo Controller connection. 
In the future, the functionality will be included in the servo control code.

these are the files for controlling the servos on the Pimoroni 2040 servo controller:
servoControl.json this contains the animations and poses that are stored on the controller for playback
(servoValues.json)
usbServosCluster.py - run the controller in cluster mode (18 servos)
usbServos.py - run the controller in conventional mode (just 16 servos)
the control code currently gets the commands via serial interface and USB-C connection
