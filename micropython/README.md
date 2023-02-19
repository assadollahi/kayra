the file interactiveServo.py should run on the PC
the file usbServos.py should run on the servo controller

usbServos will try to load the servoConfig.json, if that's not available, LED0 on the controller will turn red otherwise green.

usbServos will also try to load the servoControl.json, if not available LED1 = red otherwise green.

the default operation mode is "untethered" (LED5 = green), i.e. the controller is not connected to the PC via USB and
Kayra can perform an action when the USER button is pressed.

long pressing the USER button will turn LED5 to blue indicating that the controller board is now in "thethered" mode
and will listen to commands from the PC via USB serial.



