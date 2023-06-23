
interactiveServo.py 
- should run on the Linux PC
- is for setting servo values, defining poses and defining animations
- it also receives sensor data like from the IMU and (future:) the current sensor from the 2040 servo controller
- it sends data via USB serial to the controller
- in the future, the serial / USB connection will be replaced by I2C connection to the ESP32 Cam in Kayra's head that connects to the host via Wifi

clientWifi.py
- this is the first connection via WiFi to the ESP32, it can send commands via TCP sockets
- see it in action [here](https://youtube.com/shorts/rHDNVzmQHSk)


