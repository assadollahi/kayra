import sys
import gc
import time
import math
import json
import uselect
from pimoroni import Button
from plasma import WS2812
from servo import ServoCluster, servo2040
from bno055 import *


"""
- create servo cluster
- control it together via serial commands from PC.
- uses code from pimoroni servo 2040 examples to move servos smoothly
"""
# connect IMU
sda=machine.Pin(20) # Explorer 20 Breakout 4
scl=machine.Pin(21) # Explorer 21 Breakout 5
i2c=machine.I2C(0,sda=sda, scl=scl, freq=400000)

imuInstalled = False
try:
    imu = BNO055(i2c)
    calibrated = False
    imuInstalled = True
except:
    print("no IMU installed")

# Create the LED bar, using PIO 1 and State Machine 0
led_bar = WS2812(servo2040.NUM_LEDS, 1, 0, servo2040.LED_DATA)

# Create a list of servos for pins 0 to 3. Up to 16 servos can be created
START_PIN = servo2040.SERVO_1
END_PIN = servo2040.SERVO_18
servos = ServoCluster(pio=0, sm=0, pins=list(range(START_PIN, END_PIN + 1)))

# Enable all servos (this sets them to middle position)
servos.enable_all()
time.sleep(0.5)

# servo speeds
TOTAL_SERVOS = 18
UPDATES = 50            # How many times to update Servos per second
TIME_FOR_EACH_MOVE = 0.50  # The time to travel between each value. 32 is nice, used to be 25, lower numbers make the robot faster
UPDATES_PER_MOVE = TIME_FOR_EACH_MOVE * UPDATES # 50 * 0.32 = 16
USE_COSINE = False       # Whether or not to use a cosine path between values

# servos & poses
servoValues = [0.0] * TOTAL_SERVOS # servo values for the current posture
nextServoValues = [0.0] * TOTAL_SERVOS # servo values for the next posture provided by SAS command
poseDictionary = {} # dictionary of posture names and their servoValues
poseName = "crouch"
untetheredStartPose = "crouch"

# animation
animationDictionary = {} # dictionary of animation names and their list of poses
animationToPlay = "first"

# button for untethered mode
user_sw = Button(servo2040.USER_SW)
operationMode = "tethered"

# led bar for status display
led_bar.start()

def sendIMUToHost():
    if imuInstalled == True:
            
        '''
        if not calibrated:
            calibrated = imu.calibrated()
            print('Calibration required: sys {} gyro {} accel {} mag {}'.format(*imu.cal_status()))
        print('Temperature {}°C'.format(imu.temperature()))
        print('Mag       x {:5.0f}    y {:5.0f}     z {:5.0f}'.format(*imu.mag()))
        print('Gyro      x {:5.0f}    y {:5.0f}     z {:5.0f}'.format(*imu.gyro()))
        print('Accel     x {:5.1f}    y {:5.1f}     z {:5.1f}'.format(*imu.accel()))
        print('Lin acc.  x {:5.1f}    y {:5.1f}     z {:5.1f}'.format(*imu.lin_acc()))
        print('Gravity   x {:5.1f}    y {:5.1f}     z {:5.1f}'.format(*imu.gravity()))
        '''
        print('Heading     {:4.0f} roll {:4.0f} pitch {:4.0f}'.format(*imu.euler()))

def setSingleServo(inServos, inServoNumber, inServoValue):
    # set servo value
    inServos.value(inServoNumber, inServoValue)
                        
    # give servo time to react
    time.sleep(0.1)
    # send new data IMU to host
    sendIMUToHost() 

def setAllServos(inServos, inServoValues, inNextServoValues):
    
    for update in range(0, UPDATES_PER_MOVE):
        # Calculate how far along this movement to be
        percent_along = update / UPDATES_PER_MOVE

        if USE_COSINE:
            # Move the servo between values using cosine
            for eachServoNumber in range(0,TOTAL_SERVOS):
                inServos.to_percent(eachServoNumber, math.cos(percent_along * math.pi), 1.0, -1.0, inServoValues[eachServoNumber], inNextServoValues[eachServoNumber])
        else:
            # Move the servo linearly between values
            for eachServoNumber in range(0,TOTAL_SERVOS):
                inServos.to_percent(eachServoNumber, percent_along, 0.0, 1.0, inServoValues[eachServoNumber], inNextServoValues[eachServoNumber])                
        
        time.sleep(1.0 / UPDATES)
        # send new data IMU to host
        sendIMUToHost() 

def writeConfig():
    configDictionary = {} # store configuration: operation mode, initial pose, animation to play    
    configDictionary["operationMode"] = operationMode
    configDictionary["initialPose"] = untetheredStartPose
    configDictionary["animationToPlay"] = animationToPlay    

    with open("servoConfig.json", "w") as outfile:
        json.dump(configDictionary, outfile)
        
    led_bar.set_rgb(0, 120, 120, 0) # orange on LED0
    time.sleep(1.0)
    led_bar.set_rgb(0, 0, 120, 0) # green on LED0 
        
def writeControl():
    controlDictionary = {}
    controlDictionary.update({"animations" : animationDictionary})
    controlDictionary.update({"poses" : poseDictionary})

    with open("servoControl.json", "w") as outfile:
        json.dump(controlDictionary, outfile)    

    led_bar.set_rgb(1, 120, 120, 0) # orange on LED1
    time.sleep(1.0)
    led_bar.set_rgb(1, 0, 120, 0) # green on LED1

# load a config file telling:
# a) whether teach/tethered/PC mode or execution/untethered mode
# b) which animation to play when user button is pressed
# thus, we need a PC command to tell the system that after reboot execution is selected
# a long press should change mode back to tethered
# try to load animations

configLoaded = False
try:
    inJSON = ""
    with open("servoConfig.json", 'r') as f:
        inJSON = f.read()
        
    if inJSON != "":    
        inConfig = json.loads(inJSON)

        operationMode = inConfig["operationMode"]
        untetheredStartPose = inConfig["initialPose"]
        animationToPlay = inConfig["animationToPlay"]
        
        configLoaded = True
        print("servoConfig loaded")
        led_bar.set_rgb(0, 0, 120, 0) # green on LED0 
        
    else:
        print("servoConfig file empty")
    
except OSError:
    print("no servoConfig file found")

if configLoaded == False:
    #operationMode = "tethered" # default should be to connect via USB to teach
    poseName = "neutral" # defaults defined in the PC software
    animationName = "first" # default defined in the PC software
    led_bar.set_rgb(0, 120, 0, 0) # red on LED0

# next, try to load poses / animations
# these are usually generated by tethered interaction with the PC
# whenever the PC sending an animation, it's poses and the animation sequence are stored locally
controlLoaded = False
try:
    inJSON = ""
    with open("servoControl.json", 'r') as f:
        inJSON = f.read()
        
    if inJSON != "":    
        inDictionary = json.loads(inJSON)

        animationDictionary = inDictionary["animations"].copy()
        poseDictionary = inDictionary["poses"].copy()

        # go into neutral pose after loading poses    
        servoValues = poseDictionary[untetheredStartPose].copy()
        setAllServos(servos, servoValues, servoValues)
        
        controlLoaded = True
        print("servoControl loaded")
        led_bar.set_rgb(1, 0, 120, 0) # green on LED1
        
    else:
        print("servoControl file empty")
        
except OSError:
    print("no servoControl file found")
    
if controlLoaded == False:
    led_bar.set_rgb(1, 120, 0, 0) # red on LED1

print(str(user_sw.read()))
      
# set the controller to the respective mode
if operationMode == "untethered":
    led_bar.set_rgb(5, 0, 120, 0) # green on LED5
    
    msCounter = 0
    buttonPressed = False
    while True:
        # send new data IMU to host
        sendIMUToHost()
        time.sleep(0.1)

        # however, if the user button has been pushed, play last animation
        if user_sw.raw():
            # count how long it has been pressed
            print("button")
            msCounter += 1
            #time.sleep(0.05) # wait 50ms
            
            # check press duration
            if msCounter > 10:
            # long press
                print("long press")
                # set operationMode to 'tethered' again
                operationMode = "tethered"
                # save to file system for tethered mode after reboot
                writeConfig()
                # indicate that you understood via blue on LED5
                led_bar.set_rgb(5, 0, 0, 120)
                time.sleep(1.0)
                break
                
        else:
            # if not pressed check whether pressed before
            if msCounter > 0:
                print("counter: " + str(msCounter))
                
                # short press
                print("short press")
                
                # play animation specified in servoConfig file
                for eachPose in animationDictionary[animationToPlay]:
                    
                    # get next animation step
                    for eachServoNumber in range(0,TOTAL_SERVOS-1):
                        nextServoValues[eachServoNumber] = poseDictionary[eachPose][eachServoNumber]
                    
                    # now interpolate between the servos    
                    setAllServos(servos, servoValues, nextServoValues)
                    
                    # now copy the new values to the old state    
                    for eachServoNumber in range(0,TOTAL_SERVOS-1):
                        servoValues[eachServoNumber] = nextServoValues[eachServoNumber]
                        
                # reset button press duration counter            
                msCounter = 0
                
        
elif operationMode == "tethered":
    led_bar.set_rgb(5, 0, 0, 120) # blue on LED5
    
    while True:
        # clean up memory
        gc.collect()
        
        # send new data IMU to host
        sendIMUToHost()
        time.sleep(0.1)        

        serialList = uselect.select([sys.stdin], [], [], 0.01)
        if serialList[0]:
            # read a command from the host
            inCommand = sys.stdin.readline().strip()

            if len(inCommand)>0:
                #led_bar.set_hsv(0, 1.0, 1.0, 0.5)     

                #print(inCommand)
                inCommandSplit = inCommand.split()
                cmdString = inCommandSplit[0]
                
                if cmdString == "sss":
                    # "Set Single Servo"
                    servoNumber = int(inCommandSplit[1])
                    servoValue = float(inCommandSplit[2])
                    
                    setSingleServo(servos, servoNumber, servoValue)
                   
                elif cmdString == "sas":
                    # "Set All Servos"
                    # parse the servo values into a new array
                    for arrayNumber in range(1, len(inCommandSplit)):
                        #print("servoNumber: " + str(arrayNumber-1) + " " + inCommandSplit[arrayNumber])
                        # servos are addressed zero-based
                        #servos[arrayNumber-1].value(float(inCommandSplit[arrayNumber]))
                        
                        nextServoValues[arrayNumber-1] = float(inCommandSplit[arrayNumber])
                        
                    # now interpolate between the servos    
                    setAllServos(servos, servoValues, nextServoValues)
                        
                    # now copy the new values to the old state    
                    for eachServoNumber in range(0,TOTAL_SERVOS):
                        servoValues[eachServoNumber] = nextServoValues[eachServoNumber]
                
                elif cmdString == "snp":
                    # "Store Named Pose
                    poseName = inCommandSplit[1]
                    print("pose name: " + poseName)
                    
                    # reserve space for new pose
                    poseDictionary.update({poseName : [0.0] * TOTAL_SERVOS})
                    
                    # parse the servo values into a new pose array
                    for arrayNumber in range(2, len(inCommandSplit)):
                        #print("servoNumber: " + str(arrayNumber-2) + " " + inCommandSplit[arrayNumber])                
                        poseDictionary[poseName][arrayNumber-2] = float(inCommandSplit[arrayNumber])
                
                elif cmdString == "ssa":
                    # "Store Single Animation"
                    animationName = inCommandSplit[1]
                    listOfPoses = inCommandSplit[2:]
                    print("animation: " + animationName + ", number of poses: " + str(len(listOfPoses)))
                    animationDictionary.update({animationName : listOfPoses})
                    print("poses in animation: " + str(len(animationDictionary[animationName])))
                    
                    # store in flash
                    writeControl()
                
                elif cmdString == "psa":
                    # "Play Single Animation
                    animationName = inCommandSplit[1] 
                    
                    for eachPose in animationDictionary[animationName]:
                        
                        # get next animation step
                        for eachServoNumber in range(0,TOTAL_SERVOS):
                            nextServoValues[eachServoNumber] = poseDictionary[eachPose][eachServoNumber]
                        
                        # now interpolate between the servos    
                        setAllServos(servos, servoValues, nextServoValues)
                        
                        # now copy the new values to the old state    
                        for eachServoNumber in range(0,TOTAL_SERVOS):
                            servoValues[eachServoNumber] = nextServoValues[eachServoNumber]
                        
                elif cmdString == "tup":
                    # Transmit Untethered Pose
                    untetheredStartPose = inCommandSplit[1]
                    if untetheredStartPose in poseDictionary:
                        print("start pose in untethered mode set to " + untetheredStartPose)                     
                    else:
                        print("untethered pose unknown, defaulting to 'neutral'")
                        untetheredStartPose = "neutral"
                    # write control JSON
                    writeControl()    
                    
                elif cmdString == "tua":
                    # Transmit Untethered Animation
                    animationToPlay = inCommandSplit[1]
                    if animationToPlay in animationDictionary:
                        print("animation to play set to " + animationToPlay)
                    else:
                        print("animation to play unknown, defaulting to 'first'")
                        animationToPlay = "first"
                    # write control JSON
                    writeControl()
                    
                elif cmdString == "som":
                    # Set Operation Mode
                    # argument should be either "tethered" or "untethered"
                    if inCommandSplit[1] == "tethered":
                        operationMode = inCommandSplit[1]
                    elif inCommandSplit[1] == "untethered":
                        operationMode = inCommandSplit[1]
                    else:
                        print("Set Operation Mode, unknown Mode: " + inCommandSplit[1])
                    
                    # write config JSON
                    writeConfig()
                    
                    if operationMode == "untethered":
                        # switch mode and exit
                        led_bar.set_rgb(5, 0, 120, 0) # green on LED5
                        time.sleep(1.0)
                        break

else:
    led_bar.set_rgb(5, 120, 0, 0) # red on LED5
    print("operation mode unknown")
    
# Disable the servos
servos.disable_all()

# Turn off the LED bar
led_bar.clear()
