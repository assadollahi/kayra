# this is intended to be run from a PC

import curses
import curses.ascii
import copy
import serial
import time
import json

# servos
servoNumber = 0 # current servo to be controlled
servoValues = [0.0] * 9 # storing all servo values
servoStep = 10 # moving servo by this angle on key press

# poses
poseName = "neutral" # name of the current pose
poseHighlighted = "" # for editing animations
poseNumber = 0
poseDictionary = {} # dictionary of posture names and their servoValues
poseDictionary[poseName] = servoValues

# animation
animationName = "first"
animationStep = 0
animationPlaying = False
animationDictionary = {}
animationDictionary.update({animationName : [poseName]}) # first animation consists of the neutral pose only

# control states
inputMode = "servo" # what state should receive the keyboard input
textEntered = "" # when entering a text, store it here across key strokes
textIntent = "" # use the entered text for this intent 


def setAllServos(inServoValues):
    stringValues = [str(x) for x in inServoValues] 
    #print(("sas " + " ".join(stringValues) + "\n").encode('ASCII'))
    s.write(("sas " + " ".join(stringValues) + "\n").encode('ASCII'))   

def storeNamedPose(inPoseName, inServoValues):
    stringValues = [str(x) for x in inServoValues] 
    #print(("snp " + inPoseName + " " + " ".join(stringValues) + "\n").encode('ASCII'))
    s.write(("snp " + inPoseName + " " + " ".join(stringValues) + "\n").encode('ASCII'))  

def storeSingleAnimation(inAnimName, inListOfPoses, inPoseDictionary):
    # store single anmiation, i.e. name and list of poses
    
    # send animation's poses first
    for eachPose in inListOfPoses:
        storeNamedPose(eachPose, inPoseDictionary[eachPose])
        
    # next, send the animation name together with the sequence of poses    
    s.write(("ssa " + inAnimName + " " + " ".join(inListOfPoses) + "\n").encode('ASCII'))  

def playSingleAnimation(inAnimName):
    # play single animation
    s.write(("psa " + inAnimName + "\n").encode('ASCII'))  

def controlUI(stdscr):

    global servoNumber, servoValues, servoStep
    global poseDictionary, poseName, poseHighlighted, poseNumber
    global animationNumber, animationName, animationDictionary, animationStep
    global inputMode, textEntered, textIntent

    cursorX = 0
    cursorY = 0
    
    curses.curs_set(0) 
    stdscr.nodelay(1)
    
    while True:
        
        keypress = stdscr.getch()
        
        if keypress != curses.ERR:
            
            stdscr.clear()

            # non-character entry
            if inputMode == "servo":
                    
                if keypress == curses.KEY_RIGHT:
                    servoValues[servoNumber] += servoStep
                    stdscr.addstr(3, 4, "servo " + str(servoNumber) + " set to " + str(servoValues[servoNumber]))
                    poseDictionary[poseName] = copy.deepcopy(servoValues)
                    s.write(("sss " + str(servoNumber)+ " " + str(servoValues[servoNumber]) + "\n").encode('ASCII'))

                if keypress == curses.KEY_LEFT:
                    servoValues[servoNumber] -= servoStep
                    stdscr.addstr(3, 4, "servo " + str(servoNumber) + " set to " + str(servoValues[servoNumber]))
                    poseDictionary[poseName] = copy.deepcopy(servoValues) 
                    s.write(("sss " + str(servoNumber)+ " " + str(servoValues[servoNumber]) + "\n").encode('ASCII'))

                if keypress == curses.KEY_DOWN:
                    servoNumber += 1
                    
                    if (servoNumber > 8):
                        servoNumber = 8
                        
                    stdscr.addstr(3, 4, "servo " + str(servoNumber) + " selected: " + str(servoValues[servoNumber]))
                       
                if keypress == curses.KEY_UP:
                    servoNumber -= 1
                    
                    if (servoNumber < 0):
                        servoNumber = 0
                    
                    stdscr.addstr(3, 4, "servo " + str(servoNumber) + " selected: " + str(servoValues[servoNumber]))
            
            elif inputMode == "pose":
                
                poseNumber = 0
                noOfPoses = len(poseDictionary.keys()) 
                poseList = list(poseDictionary)
                
                try:
                    poseNumber = poseList.index(poseName)
                except:
                    poseNumber = 0
                        
                if keypress == curses.KEY_DOWN:
                    poseNumber += 1
                    
                    if (poseNumber > (noOfPoses-1)):
                        poseNumber = noOfPoses-1
                        
                    # needs to be set so that the UI can highlight that line
                    poseName = poseList[poseNumber]

                           
                if keypress == curses.KEY_UP:
                    poseNumber -= 1
                    
                    if (poseNumber < 0):
                        poseNumber = 0
                    
                    poseName = poseList[poseNumber]

                    
                if keypress == 10:
                    # transfer the pose poseName to the servo controller when hitting CR
                    servoValues = copy.deepcopy(poseDictionary[poseName])
                    stdscr.addstr(3, 4, "pose " + poseName + " selected: \t" + ", ".join([str(flt) for flt in servoValues]))   
                    setAllServos(servoValues) 
            
            elif inputMode == "animation":
                animationNumber = 0
                noOfAnimations = len(animationDictionary.keys()) 
                animationList = list(animationDictionary)
                
                try:
                    animationNumber = animationList.index(animationName)
                except:
                    animationNumber = 0
                    
                if keypress == curses.KEY_RIGHT:
                    # show next animation step, i.e. next pose in list
                    animationStep += 1
                    
                    currentPoseList = animationDictionary[animationName]
                    
                    if animationStep > (len(currentPoseList)-1):
                        animationStep = len(currentPoseList)-1
                    
                if keypress == curses.KEY_LEFT:
                    # show previous animation step, i.e. previous pose in list
                    animationStep -= 1
                    
                    currentPoseList = animationDictionary[animationName]
                    
                    if animationStep < 0:
                        animationStep = 0
                    
                if keypress == curses.KEY_DOWN:
                    # change to a next, different animation
                    animationNumber += 1
                    
                    if animationNumber > (len(animationList)-1):
                        animationNumber = len(animationList)-1    
                    
                    animationName = animationList[animationNumber]

                    # start this anmiation from beginning
                    animationStep = 0  
                       
                if keypress == curses.KEY_UP:
                    # change to the previous animation
                    animationNumber -= 1
                    
                    if animationNumber < 0:
                        animationNumber = 0               
                        
                    animationName = animationList[animationNumber]
                    
                    # start this anmiation from beginning
                    animationStep = 0   
                    
            elif inputMode == "animation_edit":
                # selecting poses to compose animation
                noOfPoses = len(poseDictionary.keys()) 
                poseList = list(poseDictionary)
                
                if keypress == curses.KEY_DOWN:
                    # change to a next, different animation
                    poseNumber += 1
                    
                    if poseNumber > (len(poseList)-1):
                        poseNumber = len(poseList)-1    
                    
                    poseHighlighted = poseList[poseNumber]
      
                if keypress == curses.KEY_UP:
                    # change to the previous animation
                    poseNumber -= 1
                    
                    if poseNumber < 0:
                        poseNumber = 0               
                        
                    poseHighlighted = poseList[poseNumber]
                    
                if keypress == 10:
                    animationDictionary[animationName].append(poseHighlighted)

            # in any other mode than text input, you can load and save 
            if not(inputMode == "text"):
                
                if keypress == ord('q'):
                    # leave app
                    return False    
                
                if keypress == ord('l'):
                    stdscr.addstr(3, 4, "loading values")
                    with open("servoControl.json", 'r') as f:
                        inDictionary = json.load(f)
                    
                    animationDictionary = copy.deepcopy(inDictionary["animations"])
                    poseDictionary = copy.deepcopy(inDictionary["poses"])
                    
                    # go into neutral pose after loading poses    
                    servoValues = copy.deepcopy(poseDictionary["neutral"])
                    setAllServos(servoValues)
                    
                if keypress == ord('s'):
                    stdscr.addstr(3, 4, "saving values")
                    
                    outDictionary = {}
                    outDictionary.update({"animations" : animationDictionary})
                    outDictionary.update({"poses" : poseDictionary})
                    
                    with open("servoControl.json", "w") as outfile:
                        json.dump(outDictionary, outfile)
                        
            if inputMode == "servo":
                # control mode in pose, i.e. change the servo values for the current pose
                #stdscr.addstr(2, 4, "control mode for pose " + poseName)
                
                if keypress == ord('1'):
                    servoStep = 1
                    stdscr.addstr(3, 4, "servoStep set to " + str(servoStep))     
                
                if keypress == ord('5'):
                    servoStep = 5
                    stdscr.addstr(3, 4, "servoStep set to " + str(servoStep))         
                
                if keypress == ord('0'):
                    servoStep = 10
                    stdscr.addstr(3, 4, "servoStep set to " + str(servoStep))     
                
                if keypress == ord('z'):
                    stdscr.addstr(3, 4, "set servo " + str(servoNumber) + " to zero")
                    servoValues[servoNumber] = 0
                    s.write(("sss " + str(servoNumber)+ " " + str(servoValues[servoNumber]) + "\n").encode('ASCII'))     
                                
                if keypress == ord('p'):
                    inputMode = "pose"
                                
                if keypress == ord('a'):
                    inputMode = "animation"
            
            elif inputMode == "text":
                # mode for entering text
                #stdscr.addstr(2, 4, "text input mode")
                
                if curses.ascii.isalnum(keypress):
                    textEntered += chr(keypress)
                    stdscr.addstr(4, 4, textEntered)
                else:
                    
                    if keypress == 10:
                
                        if textIntent == "pose":
                            poseName = textEntered
                            # default servoValues of the new pose are the current servo values
                            poseDictionary[poseName] = copy.deepcopy(servoValues)
                            stdscr.addstr(3, 4, "servo pose " + poseName + " added & selected")
                            inputMode = "pose"
                            
                        elif textIntent == "animation":
                            animationName = textEntered
                            animationDictionary.update({animationName : []})
                            stdscr.addstr(3, 4, "animation " + animationName + " added & selected")
                            inputMode = "animation"
                                
                        else:
                            stdscr.addstr(3, 4, "unknown text intent: " + textIntent)
                            inputMode = "servo"
                    else:
                        stdscr.addstr(4, 4, "not an ascii char and not return")
                
            elif inputMode == "pose":
                # mode for navigating & editing poses
                #stdscr.addstr(2, 4, "pose mode")
                
                if keypress == ord('c'):
                    inputMode = "servo"
                                
                if keypress == ord('a'):
                    inputMode = "animation"
                
                if keypress == ord('t'):
                    # transmit pose, i.e. send the current pose to controller to be stored there
                    servoValuesToBeSent = copy.deepcopy(poseDictionary[poseName])
                    stdscr.addstr(3, 4, "store named pose " + poseName + " \t" + ", ".join([str(flt) for flt in servoValuesToBeSent]))
                    storeNamedPose(poseName, servoValuesToBeSent)                  
                
                if keypress == ord('+'):
                    # add a new pose
                    stdscr.addstr(3, 4, "enter name for new pose")
                    inputMode = "text"
                    textEntered = ""
                    textIntent = "pose"

            elif inputMode == "animation":
                # animation mode: toggle between animations and step through their poses
                
                if keypress == ord('c'):
                    inputMode = "servo"
                    
                if keypress == ord('p'):
                    inputMode = "pose"
                    
                if keypress == ord('e'):
                    inputMode = "animation_edit"
                    
                if keypress == ord('t'):
                    # transmit animation, i.e. send the current animation to controller to be stored there
                    animationToBeSent = copy.deepcopy(animationDictionary[animationName])
                    stdscr.addstr(3, 4, "store named animation " + animationName + " \t" + ", ".join(animationToBeSent))
                    storeSingleAnimation(animationName, animationToBeSent, poseDictionary)  

                if keypress == 10:
                    # playback animation when hitting CR (animation has to be transferred via key "t" before)
                    stdscr.addstr(3, 4, "playing back animation " +  animationName)
                    playSingleAnimation(animationName)
                    
                if keypress == ord('x'):
                    stdscr.addstr(3, 4, "stopping play back of animation " +  animationName)
                                
                if keypress == ord('+'):
                    # add a new animation
                    stdscr.addstr(3, 4, "enter name for new animation:")
                    inputMode = "text"
                    textEntered = ""
                    textIntent = "animation"
                    
                      
            elif inputMode == "animation_edit":
                # editing animations: adding and removing poses for a single animation
                                
                if keypress == ord('c'):
                    inputMode = "servo"
                    
                if keypress == ord('p'):
                    inputMode = "pose"
                
                if keypress == ord('a'):
                    inputMode = "animation"
                    
            else:
                stdscr.addstr(3, 4, "unknown inputMode")
                inputMode = "servo"    
        
        if inputMode == "servo":
            # control mode in pose, i.e. change the servo values for the current pose
            stdscr.addstr(2, 4, "control mode for pose " + poseName)
            # print out overview
            stdscr.addstr(4, 4, "list of all poses:")

            lineCounter = 5
            for eachSingleServo in servoValues:
                servoNumberToDisplay = lineCounter - 5
                if servoNumberToDisplay == servoNumber:
                    stdscr.addstr(lineCounter, 4, str(servoNumberToDisplay) + ": " + str(eachSingleServo), curses.A_REVERSE)
                else:
                    stdscr.addstr(lineCounter, 4, str(servoNumberToDisplay) + ": " + str(eachSingleServo))
                lineCounter += 1
            
        elif inputMode == "text":
            # mode for entering text
            stdscr.addstr(2, 4, "text input mode")
            
        elif inputMode == "pose":
            # mode for navigating & editing poses
            stdscr.addstr(2, 4, "pose mode")
            
            # print out overview
            stdscr.addstr(4, 4, "servo values:")
            poseList = list(poseDictionary)
            lineCounter = 5
            for eachSinglePose in poseList:
                strValues = [str(singleValue) for singleValue in poseDictionary[eachSinglePose]] 
                if eachSinglePose == poseName:
                    stdscr.addstr(lineCounter, 4, eachSinglePose + ":\t" + "\t".join(strValues), curses.A_REVERSE)
                else:
                    stdscr.addstr(lineCounter, 4, eachSinglePose + ":\t" + "\t".join(strValues))
                lineCounter += 1
     
        elif inputMode == "animation":
            # animation mode: toggle between animations and step through their poses
            stdscr.addstr(2, 4, "animation mode") 
            stdscr.addstr(4, 4, "animations and their poses:")
            
            animationList = list(animationDictionary)
            lineCounter = 5
            for eachSingleAnim in animationList:
                if eachSingleAnim == animationName:
                    stdscr.addstr(lineCounter, 4, eachSingleAnim + ":\t" + "\t".join(animationDictionary[eachSingleAnim]), curses.A_REVERSE)
                else:
                    stdscr.addstr(lineCounter, 4, eachSingleAnim + ":\t" + "\t".join(animationDictionary[eachSingleAnim]))
                lineCounter += 1  
        
        elif inputMode == "animation_edit":
            stdscr.addstr(2, 4, "animation edit mode") 
            
            stdscr.addstr(3, 4, animationName + ":\t" + "\t".join(animationDictionary[animationName]))
            
            stdscr.addstr(4, 4, "available poses:")
            poseList = list(poseDictionary)
            lineCounter = 5
            for eachSinglePose in poseList:
                strValues = [str(singleValue) for singleValue in poseDictionary[eachSinglePose]] 
                if eachSinglePose == poseHighlighted:
                    stdscr.addstr(lineCounter, 4, eachSinglePose + ":\t" + "\t".join(strValues), curses.A_REVERSE)
                else:
                    stdscr.addstr(lineCounter, 4, eachSinglePose + ":\t" + "\t".join(strValues))
                lineCounter += 1 
                                   
        time.sleep(0.05)

# open a serial connection
# please make sure to select the correct ACM0,1,n
s = serial.Serial("/dev/ttyACM0", 115200)

curses.wrapper(controlUI)

