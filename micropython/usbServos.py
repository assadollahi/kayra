import sys
import time
import math
from pimoroni import Button
from plasma import WS2812
from servo import Servo, servo2040

"""
- create multiple Servo objects
- control them together via serial commands from PC.
- uses code from pimoroni servo 2040 examples to move servos smoothly
"""

# Create the LED bar, using PIO 1 and State Machine 0
led_bar = WS2812(servo2040.NUM_LEDS, 1, 0, servo2040.LED_DATA)

# Create a list of servos for pins 0 to 3. Up to 16 servos can be created
START_PIN = servo2040.SERVO_1
END_PIN = servo2040.SERVO_9
servos = [Servo(i) for i in range(START_PIN, END_PIN + 1)]

# Enable all servos (this puts them at the middle)
for s in servos:
    s.enable()
time.sleep(1)

UPDATES = 50            # How many times to update Servos per second
TIME_FOR_EACH_MOVE = 0.5  # The time to travel between each values
UPDATES_PER_MOVE = TIME_FOR_EACH_MOVE * UPDATES
USE_COSINE = True       # Whether or not to use a cosine path between values

servoValues = [0.0] * 9 # servo values for the current posture
nextServoValues = [0.0] * 9 # servo values for the next posture provided by SAS command
poseDictionary = {} # dictionary of posture names and their servoValues

animationDictionary = {} # dictionary of animation names and their list of poses

# Create the user button
user_sw = Button(servo2040.USER_SW)

# Start updating the LED bar
led_bar.start()


def setSingleServo(inServos, inServoNumber, inServoValue):
    # set servo value
    inServos[inServoNumber].value(inServoValue)
                        
    # give servo time to react
    time.sleep(0.1)

def setAllServos(inServos, inServoValues, inNextServoValues):
    
    for update in range(0, UPDATES_PER_MOVE):
        # Calculate how far along this movement to be
        percent_along = update / UPDATES_PER_MOVE

        if USE_COSINE:
            # Move the servo between values using cosine
            for eachServoNumber in range(0,9):
                inServos[eachServoNumber].to_percent(math.cos(percent_along * math.pi), 1.0, -1.0, inServoValues[eachServoNumber], inNextServoValues[eachServoNumber])
        else:
            # Move the servo linearly between values
            for eachServoNumber in range(0,9):
                inServos[eachServoNumber].to_percent(percent_along, 0.0, 1.0, inServoValues[eachServoNumber], inNextServoValues[eachServoNumber])                
        
        time.sleep(1.0 / UPDATES)
        



# receive command "servoNumber servoValue"
while not user_sw.raw():
    
    # read a command from the host
    inCommand = sys.stdin.readline().strip()
    
    # if you received a command, show via led0
    if len(inCommand) > 0:
        led_bar.set_hsv(0, 1.0, 1.0, 0.5)     

        print(inCommand)
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
            for eachServoNumber in range(0,9):
                servoValues[eachServoNumber] = nextServoValues[eachServoNumber]
        
        elif cmdString == "snp":
            # "Store Named Pose
            poseName = inCommandSplit[1]
            print("pose name: " + poseName)
            
            # reserve space for new pose
            poseDictionary.update({poseName : [0.0] * 9})
            
            # parse the servo values into a new pose array
            for arrayNumber in range(2, len(inCommandSplit)):
                #print("servoNumber: " + str(arrayNumber-2) + " " + inCommandSplit[arrayNumber])                
                poseDictionary[poseName][arrayNumber-2] = float(inCommandSplit[arrayNumber])
        
        elif cmdString == "ssa":
            # "Store Single Animation"
            animName = inCommandSplit[1]
            listOfPoses = inCommandSplit[2:]
            print("animation: " + animName + ", number of poses: " + str(len(listOfPoses)))
            animationDictionary.update({animName : listOfPoses})
        
        elif cmdString == "psa":
            # "Play Single Animation
            animName = inCommandSplit[1] 
            
            for eachPose in animationDictionary[animName]:
                
                # get next animation step
                for eachServoNumber in range(0,9):
                    nextServoValues[eachServoNumber] = poseDictionary[eachPose][eachServoNumber]
                
                # now interpolate between the servos    
                setAllServos(servos, servoValues, nextServoValues)
                
                # now copy the new values to the old state    
                for eachServoNumber in range(0,9):
                    servoValues[eachServoNumber] = nextServoValues[eachServoNumber]
                
                '''
                for eachServoNumber in range(0,9):
                    #print("servoNumber: " + str(arrayNumber-1) + " " + inCommandSplit[arrayNumber])
                    # servos are addressed zero-based
                    servos[eachServoNumber].value(poseDictionary[eachPose][eachServoNumber])
            
                # wait 200ms for servos to settle between each pose
                time.sleep(0.2)
                '''
        
        # indicate that you received a cmd
        led_bar.set_hsv(0, 0.0, 0.0, 0.0)
    
# Disable the servos
for s in servos:
    s.disable()

# Turn off the LED bar
led_bar.clear()
