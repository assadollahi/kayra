# this is intended to be run from a PC
# please pip3 install pynput 

from pynput import keyboard
import serial
import time
import json

servoNumber = 0
servoValues = [0.0] * 4

def on_press(key):
    global servoNumber, servoValues
    
    if key == keyboard.Key.esc:
        # Stop listener
        return False    

    if key == keyboard.Key.right:
        servoValues[servoNumber] += 10
        s.write((str(servoNumber)+ " " + str(servoValues[servoNumber]) + "\n").encode('ASCII'))

    if key == keyboard.Key.left:
        servoValues[servoNumber] -= 10
        s.write((str(servoNumber)+ " " + str(servoValues[servoNumber]) + "\n").encode('ASCII'))

    if key == keyboard.Key.up:
        servoNumber += 1
        
        if (servoNumber > 3):
            servoNumber = 3
           
    if key == keyboard.Key.down:
        servoNumber -= 1
        
        if (servoNumber < 0):
            servoNumber = 0
            
    if hasattr(key, 'char'):
        if key.char == 'l':
            print("loading values")
            with open("servoValues.json", 'r') as f:
                servoDictionary = json.load(f)
            servoValues = servoDictionary["neutral"]
            
            for eachServo in range(0, len(servoValues)):
                s.write((str(eachServo)+ " " + str(servoValues[eachServo]) + "\n").encode('ASCII'))

        if key.char == 's':
            print("saving values")
            servoDictionary = {"neutral" : servoValues}
            with open("servoValues.json", "w") as outfile:
                json.dump(servoDictionary, outfile)
            servoValues = servoDictionary["neutral"]
        
# open a serial connection
# please make sure to select the correct ACM0,1,n
s = serial.Serial("/dev/ttyACM1", 115200)

# Collect events until released
with keyboard.Listener(
    suppress=True,
    on_press=on_press) as listener:
    listener.join()

