This is the directory that contains the software for the ESP32 Cam.
Here, we keep the display software, the Wifi Connection and the camera server as well as the I2C connection to the body / servo controller.

commandViaWifiToI2C.py  
this is the code that receives commands via Wifi and sends them via I2C to the servo controller 
for autonomous operation, rename this file to main.py to be started after ESP32's boot up.

connectWifi.py 
this is the code that simply connects to Wifi
for autonomous operation, rename this file to booty.py to connect to Wifi at boot time and before running main.py
here, you have to specify your SSID and wifi password.
please note thate the ESP32 Cam only connects to 2.4GHz networks, not to 5GHz networks!

the tools directory contains software that 
is a simple wifi server sending / receiving data via sockets
is listing all connected i2c devices
is sending a command to a specified i2c device
