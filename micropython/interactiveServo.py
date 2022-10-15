# this is intended to be run from a PC
# please pip3 install pynput 

from pynput import keyboard
import copy
import serial
import time
import json

servoDictionary = {} # dictionary of posture names and their servoValues
poseName = "neutral" # name of the current pose
servoNumber = 0 # current servo to be controlled
servoValues = [0.0] * 9 # servo values for the current posture
servoStep = 10

# start with the neutral pose
servoDictionary["neutral"] = servoValues

inputMode = "control"
textEntered = ""
textIntent = ""

def on_press(key):

    global servoDictionary, poseName
    global servoNumber, servoValues, servoStep
    global inputMode, textEntered, textIntent
    
    # meta commands
    if key == keyboard.Key.esc:
        # Stop listener
        return False    

    if key == keyboard.Key.insert:
        print("text input mode")
        textEntered = ""
        inputMode = "text"
        
    if key == keyboard.Key.enter:
        #print("text entered: " + textEntered)
                
        if textIntent == "pose":
            poseName = textEntered
            # default servoValues of the new pose are the current servo values
            servoDictionary[poseName] = copy.deepcopy(servoValues)
            print("servo pose " + poseName + " added & selected")
            inputMode = "pose"
            
        else:
            print("unknown text intent: " + textIntent)
            inputMode = "control"

    # non-character entry
    if inputMode == "control":
            
        if key == keyboard.Key.right:
            servoValues[servoNumber] += servoStep
            print("servo " + str(servoNumber) + " set to " + str(servoValues[servoNumber]))
            servoDictionary[poseName] = copy.deepcopy(servoValues)
            s.write((str(servoNumber)+ " " + str(servoValues[servoNumber]) + "\n").encode('ASCII'))

        if key == keyboard.Key.left:
            servoValues[servoNumber] -= servoStep
            print("servo " + str(servoNumber) + " set to " + str(servoValues[servoNumber]))
            servoDictionary[poseName] = copy.deepcopy(servoValues) 
            s.write((str(servoNumber)+ " " + str(servoValues[servoNumber]) + "\n").encode('ASCII'))

        if key == keyboard.Key.up:
            servoNumber += 1
            
            if (servoNumber > 8):
                servoNumber = 8
                
            print("servo " + str(servoNumber) + " selected: " + str(servoValues[servoNumber]))
               
        if key == keyboard.Key.down:
            servoNumber -= 1
            
            if (servoNumber < 0):
                servoNumber = 0
            
            print("servo " + str(servoNumber) + " selected: " + str(servoValues[servoNumber]))
    
    elif inputMode == "pose":
        
        poseNumber = 0
        noOfPoses = len(servoDictionary.keys()) 
        poseList = list(servoDictionary)
        
        try:
            poseNumber = poseList.index(poseName)
        except:
            poseNumber = 0
                
        if key == keyboard.Key.up:
            poseNumber += 1
            
            if (poseNumber > (noOfPoses-1)):
                poseNumber = noOfPoses-1
            
            poseName = poseList[poseNumber]
            servoValues = copy.deepcopy(servoDictionary[poseName])
            print("pose " + poseName + " selected: \t" + ", ".join([str(flt) for flt in servoValues]))
            for eachServo in range(0, len(servoValues)):
                s.write((str(eachServo)+ " " + str(servoValues[eachServo]) + "\n").encode('ASCII'))
                   
        if key == keyboard.Key.down:
            poseNumber -= 1
            
            if (poseNumber < 0):
                poseNumber = 0
            
            poseName = poseList[poseNumber]
            servoValues = copy.deepcopy(servoDictionary[poseName])
            print("pose " + poseName + " selected: \t" + ", ".join([str(flt) for flt in servoValues]))   
            for eachServo in range(0, len(servoValues)):
                s.write((str(eachServo)+ " " + str(servoValues[eachServo]) + "\n").encode('ASCII'))   
      
    # character entry
    if hasattr(key, 'char'):

        # in any other mode than text input, you can load and save 
        if not(inputMode == "text"):
            if key.char == 'l':
                print("loading values")
                with open("servoValues.json", 'r') as f:
                    servoDictionary = json.load(f)
                
                # go into neutral pose after loading poses    
                servoValues = copy.deepcopy(servoDictionary["neutral"])
                for eachServo in range(0, len(servoValues)):
                    s.write((str(eachServo)+ " " + str(servoValues[eachServo]) + "\n").encode('ASCII'))

            if key.char == 's':
                print("saving values")
                with open("servoValues.json", "w") as outfile:
                    json.dump(servoDictionary, outfile)
                
        
        if inputMode == "control":
            if key.char == '1':
                servoStep = 1
                print("servoStep set to " + str(servoStep))     
            
            if key.char == '5':
                servoStep = 5
                print("servoStep set to " + str(servoStep))         
            
            if key.char == '0':
                servoStep = 10
                print("servoStep set to " + str(servoStep))     
            
            if key.char == 'z':
                print("set servo " + str(servoNumber) + " to zero")
                servoValues[servoNumber] = 0
                s.write((str(servoNumber)+ " " + str(servoValues[servoNumber]) + "\n").encode('ASCII'))     
                            
            if key.char == 'p':
                print("entering pose mode\n\tcursor up and down to toggle poses")
                inputMode = "pose"
        
        elif inputMode == "text":
            print(key.char)
            textEntered += key.char
            
        elif inputMode == "pose":
            if key.char == 'c':
                print("entering control mode for pose " + poseName + "\n\tcursor up and down to toggle servoNumber, left and right to change values")
                inputMode = "control"
                
            if key.char == '+':
                print("adding a new pose\n\ttype its name followed by enter")
                inputMode = "text"
                textEntered = ""
                textIntent = "pose"
            
        else:
            print("unknown inputMode")
            inputMode = "control"    
    
# open a serial connection
# please make sure to select the correct ACM0,1,n
s = serial.Serial("/dev/ttyACM1", 115200)

# Collect events until released
#    suppress=True,
with keyboard.Listener(

    on_press=on_press) as listener:
    listener.join()

