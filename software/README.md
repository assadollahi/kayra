
servoMap.json — which servo channel is which joint:
- the host, the servo controller and the MuJoCo simulation all talk about servos as
  an 18 float vector. servoMap.json is the single place that says what each position
  in that vector means, what the joint is called, how far it may travel and which
  MuJoCo actuator it drives.
- convention: even index = right side, odd index = left side, ordered bottom up per leg.
  0/1 ankles, 2/3 knees, 4/5 hip pitch, 6/7 hip yaw, 8..13 arms, 14/15 unused,
  16 pelvis rotation, 17 head pitch.
- servoMapLib.py is the loader used by the host software and by the simulation.
  the servo controller reads servoMap.json directly, so copy that file to the board
  next to servoConfig.json and servoControl.json. LED2 turns green when it was loaded
  and red when it is missing. without it the controller still runs, but it will not
  enforce any servo limits.
- the entries for the arms and the pelvis are marked "verified": false, they are
  inferred from the pose library and still have to be confirmed on the real robot,
  see host/tools/identifyServo.py below. the min / max values are marked
  "limitsVerified": false, they are derived from the poses in servoControl.json plus
  a margin and are not measured mechanical limits.

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
- usbServosCluster will also try to load the servoMap.json, if not available LED2 = red otherwise green. without it the servo limits are not enforced.
- the default operation mode is "untethered" (LED5 = green), i.e. the controller is not connected to the PC via USB and Kayra can perform an action when the USER button is pressed.
- long pressing the USER button will turn LED5 to blue indicating that the controller board is now in "thethered" mode and will listen to commands from the PC via USB serial.

3) host/tools/identifyServo.py:
- runs on the Linux PC, controller in tethered mode
- moves one servo channel at a time so you can see which joint it belongs to
- 'n <name>' confirms the joint of a channel, 'min' / 'max' record the mechanical
  limits after carefully jogging towards a hard stop, 'w' writes servoMap.json
- it deliberately ignores the software limits, that is the only way to widen them.
  use step size 1 near a hard stop.

4) understanding the serial ports:
- host/tools/serialPortInfo.py runs on LinuxPC and lists all available serial Ports
- robot/tools/serialSendText.py runs on the Pimoroni 2040 Servo controller and will send text to the Linux PC

5) robot/tools/i2cTest.py:
- runs on micropython devices and will list all connected i2c devices to find their address

6) robot/sensors/ imuTest.py, bno055.py, bno055_base.py:
- it is the standalone IMU readout software printing to USB serial
- the IMU is connected via i2c, hence the test code in #5.
- the code from main.py is used in #2 to read the IMU and send it to #1


setting up the host PC:

1) serial port permission. the servo controller shows up as /dev/ttyACM0, owned by
   root:dialout, so your user has to be in that group or every connection fails with
   a permission error:
     sudo usermod -aG dialout $USER
   log out and back in afterwards, group changes do not apply to running shells.

2) on Ubuntu 24.04 and later python ships without pip and without ensurepip, so
   'python3 -m venv' would create an environment with no pip in it:
     sudo apt install python3-venv

3) virtual environment, one at the top of the repository serves everything:
     python3 -m venv .venv
     source .venv/bin/activate          # or activate.fish
     pip install -r software/requirements.txt      # host: pyserial, numpy
     pip install -r mujoco/requirements.txt        # only if you want the simulation
   .venv is in .gitignore.

4) 'pip list' should now show the packages, 'pip freeze' gives you the exact
   versions if you ever need to reproduce a setup.

note: do not run python from the top of the repository without the virtual
environment, the mujoco directory shadows the mujoco library and 'import mujoco'
will silently pick up the directory instead.
