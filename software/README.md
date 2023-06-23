
we have two directories host and robot:
- host is the PC with good computing capabilities, tested on Ubuntu, all software in Python
- robot is intended to run at Kayra, including Wifi connection, camera, servo controller and sensors

basic operation:
1) host/interactiveServo.py 
- should run on the Linux PC
- is for setting servo values, defining poses and defining animations
- it sends data via USB serial to the controller

2) robot/body/ usbServosCluster.py / usbServos.py 
- should run on the Pimoroni 2040 servo controller
- the Cluster variant is the current, it controls the servos via ServoCluster and can handle 18 servos, the other is the "traditional" way to control servos, but only up to 16.
- it is listening on the USB serial for commands
- it can store poses and animations on the local flash
- it allows for untethered opperation via user button and the stored animations
- rename this file on the controller to main.py to run it automatically and without Thonny IDE.

interaction of the two softwares:
- usbServos will try to load the servoConfig.json, if that's not available, LED0 on the controller will turn red otherwise green.
- usbServos will also try to load the servoControl.json, if not available LED1 = red otherwise green.
- the default operation mode is "untethered" (LED5 = green), i.e. the controller is not connected to the PC via USB and Kayra can perform an action when the USER button is pressed.
- long pressing the USER button will turn LED5 to blue indicating that the controller board is now in "thethered" mode and will listen to commands from the PC via USB serial.

3) understanding the serial ports:
- host/tools/serialPortInfo.py runs on LinuxPC and lists all available serial Ports
- robot/tools/serialSendText.py runs on the Pimoroni 2040 Servo controller and will send text to the Linux PC

4) robot/tools/i2cTest.py:
- runs on micropython devices and will list all connected i2c devices to find their address

5) robot/sensors/ imuTest.py, bno055.py, bno055_base.py:
- it is the standalone IMU readout software printing to USB serial
- the IMU is connected via i2c, hence the test code in #4.
- the code from main.py is used in #2 to read the IMU and send it to #1


