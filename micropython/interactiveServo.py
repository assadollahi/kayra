# this is intended to be run from a PC

import curses
import curses.ascii
import copy
import serial
import serial.tools.list_ports
import time
import json

# connections
currentPort = 0 # first serial port 
serialPort = -1

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
inputMode = "connect" # what state should receive the keyboard input
textEntered = "" # when entering a text, store it here across key strokes
textIntent = "" # use the entered text for this intent 

def sendCommand(inCommand):
    # this should be the only place where commands are sent 
    # so this would be the place to connect to other controllers
    global serialPort

    '''
    if serialPort == -1:
        inputMode = "connect"
    else:
    '''    
    serialPort.write((inCommand + "\n").encode('ASCII'))

def setAllServos(inServoValues):
    stringValues = [str(x) for x in inServoValues] 
    sendCommand("sas " + " ".join(stringValues) + "\n")   

def storeNamedPose(inPoseName, inServoValues):
    stringValues = [str(x) for x in inServoValues] 
    sendCommand("snp " + inPoseName + " " + " ".join(stringValues) + "\n")

def storeSingleAnimation(inAnimName, inListOfPoses, inPoseDictionary):
    # store single anmiation, i.e. name and list of poses
    
    # send animation's poses first
    for eachPose in inListOfPoses:
        storeNamedPose(eachPose, inPoseDictionary[eachPose])
        
    # next, send the animation name together with the sequence of poses    
    sendCommand("ssa " + inAnimName + " " + " ".join(inListOfPoses) + "\n") 

def playSingleAnimation(inAnimName):
    # play single animation
    sendCommand("psa " + inAnimName + "\n") 

def setUntetheredAnimation(inAnimName):
    # set animation to be played when untethered and user button is pressed
    sendCommand("sua " + inAnimName + "\n")

def controlUI(stdscr):

    global currentPort, serialPort
    global servoNumber, servoValues, servoStep
    global poseDictionary, poseName, poseHighlighted, poseNumber
    global animationNumber, animationName, animationDictionary, animationStep
    global inputMode, textEntered, textIntent

    cursorX = 0
    cursorY = 0
    
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)    
    curses.curs_set(0) 
    stdscr.nodelay(1)
    
    while True:
        
        keypress = stdscr.getch()
        
        if keypress != curses.ERR:
            
            stdscr.clear()

            # non-character entry
            if inputMode == "connect":
                # connect controller via serial port 
                noOfPorts = len(serial.tools.list_ports.comports())
                
                # up / down for flipping through connections, enter for selecting a connection
                if keypress == curses.KEY_DOWN:
                    currentPort += 1
                    
                    if currentPort > (noOfPorts-1):
                        currentPort = noOfPorts-1
                    
                    stdscr.addstr(3, 4, "port " + str(currentPort) + " selected")
                    
                if keypress == curses.KEY_UP:
                    currentPort -= 1
                    
                    if currentPort < 0:
                        currentPort = 0
                    
                    stdscr.addstr(3, 4, "port " + str(currentPort) + " selected")
                
            elif inputMode == "pose_edit":
                    
                if keypress == curses.KEY_RIGHT:
                    servoValues[servoNumber] += servoStep
                    stdscr.addstr(3, 4, "servo " + str(servoNumber) + " set to " + str(servoValues[servoNumber]))
                    poseDictionary[poseName] = copy.deepcopy(servoValues)
                    sendCommand("sss " + str(servoNumber)+ " " + str(servoValues[servoNumber])) 

                if keypress == curses.KEY_LEFT:
                    servoValues[servoNumber] -= servoStep
                    stdscr.addstr(3, 4, "servo " + str(servoNumber) + " set to " + str(servoValues[servoNumber]))
                    poseDictionary[poseName] = copy.deepcopy(servoValues) 
                    sendCommand("sss " + str(servoNumber)+ " " + str(servoValues[servoNumber]))

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
                        json.dump(outDictionary, outfile, indent=4)
                        
                if keypress == ord('u'):
                    # prepare controller for disconnect from PC and 
                    # change its operationMode to 'untethered' to play the stored animation
                    # to store an animation, press 'p' when in animation mode 
                    stdscr.addstr(3, 4, "setting controller to 'untethered', PC connection won't work after reboot, long press user button to change back to 'tethered'. ") 
                    sendCommand("som untethered\n")             
                        
            if inputMode == "connect":
                if keypress == 10:
                    ports = serial.tools.list_ports.comports()
                    stdscr.addstr(3, 4, "connecting to " + ports[currentPort].description) 
                    # open selected serial connection, e.g. "/dev/ttyACM1"
                    serialPort = serial.Serial(ports[currentPort].device, 115200)
                    inputMode = "connect"
                    
                if keypress == ord('p'):
                    inputMode = "pose"
                                
                if keypress == ord('a'):
                    inputMode = "animation"                    
            
            elif inputMode == "pose_edit":
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
                    sendCommand("sss " + str(servoNumber)+ " " + str(servoValues[servoNumber]) + "\n")     
                                
                if keypress == ord('p'):
                    inputMode = "pose"
                                
                if keypress == ord('a'):
                    inputMode = "animation"
            
            elif inputMode == "text":
                # mode for entering text
                #stdscr.addstr(1, 4, str(keypress))
                
                if curses.ascii.isalnum(keypress):
                    textEntered += chr(keypress)
                    stdscr.addstr(4, 4, textEntered)

                else:
                    
                    if keypress == curses.KEY_BACKSPACE: 
                        #remove last char 
                        textEntered = textEntered[:-1]
                        stdscr.addstr(4, 4, textEntered)
                        
                    elif keypress == 10:
                        # depending on the intent for which text input 
                        # mode was switched on, use the enteredText
                        
                        if textIntent == "pose_del":
                            if textEntered == "y":
                                del poseDictionary[poseName]
                                stdscr.addstr(3, 4, "pose " + poseName + " removed")
                                poseName = "neutral"
                            
                            inputMode = "pose"
                
                        elif textIntent == "pose_rename":
                            if textEntered in poseDictionary.keys():
                                # don't try to overwrite an existing key
                                stdscr.addstr(3, 4, "renaming " + poseName + " not possible, new pose name " + textEntered + " already exists.", curses.color_pair(2))
                                inputMode = "pose"
                            else:
                                # make a copy of the pose with the new name, delete the pose with the old name
                                oldPoseName = poseName
                                poseName = textEntered
                                poseDictionary[poseName] = copy.deepcopy(poseDictionary[oldPoseName])                                
                                del poseDictionary[oldPoseName]
                                
                                stdscr.addstr(3, 4, "pose " + oldPoseName + " renamed into " + poseName, curses.color_pair(1))
                                inputMode = "pose"
                            
                        elif textIntent == "pose":
                            poseName = textEntered
                            # default servoValues of the new pose are the current servo values
                            poseDictionary[poseName] = copy.deepcopy(servoValues)
                            stdscr.addstr(3, 4, "pose " + poseName + " added & selected", curses.color_pair(1))
                            inputMode = "pose"
                        
                        elif textIntent == "animation_del":
                            if textEntered == "y":
                                del animationDictionary[animationName]
                                stdscr.addstr(3, 4, "animation " + animationName + " removed", curses.color_pair(1))
                                animationName = "first"
                            
                            inputMode = "animation"
                
                        elif textIntent == "animation_rename":
                            if textEntered in animationDictionary.keys():
                                # don't try to overwrite an existing key
                                stdscr.addstr(3, 4, "renaming " + animationName + " not possible, new animation name " + textEntered + " already exists.", curses.color_pair(2))
                                inputMode = "animation"
                            else:
                                # make a copy of the pose with the new name, delete the pose with the old name
                                oldAnimationName = animationName
                                animationName = textEntered
                                animationDictionary[animationName] = copy.deepcopy(animationDictionary[oldAnimationName])                                
                                del animationDictionary[oldAnimationName]
                                
                                stdscr.addstr(3, 4, "animation " + oldAnimationName + " renamed into " + animationName, curses.color_pair(1))
                                inputMode = "animation"
                            
                        elif textIntent == "animation":
                            animationName = textEntered
                            animationDictionary.update({animationName : []})
                            stdscr.addstr(3, 4, "animation " + animationName + " added & selected", curses.color_pair(1))
                            inputMode = "animation"
                                
                        else:
                            stdscr.addstr(3, 4, "unknown text intent: " + textIntent, curses.color_pair(2))
                            inputMode = "pose_edit"
                            
                    else:
                        stdscr.addstr(4, 4, textEntered)
                        stdscr.addstr(5, 4, "not an ascii char and not backspace or enter", curses.color_pair(2))
                
            elif inputMode == "pose":
                # mode for navigating & editing poses
                stdscr.addstr(2, 4, "pose mode")
                
                if keypress == ord('e'):
                    inputMode = "pose_edit"
                                
                if keypress == ord('a'):
                    inputMode = "animation"
                    
                if keypress == ord('d'):
                    # remove pose, but ask before deleting
                    stdscr.addstr(3, 4, "delete pose " + poseName + " (y)?")
                    inputMode = "text"
                    textEntered = ""
                    textIntent = "pose_del"                    
                
                if keypress == ord('r'):
                    # rename pose
                    stdscr.addstr(3, 4, "rename pose " + poseName + ":")
                    inputMode = "text"
                    textEntered = ""
                    textIntent = "pose_rename"                    
                
                if keypress == ord('t'):
                    # store untethered pose
                    # 
                    servoValuesToBeSent = copy.deepcopy(poseDictionary[poseName])
                    storeNamedPose(poseName, servoValuesToBeSent) 
                    stdscr.addstr(3, 4, "transmit pose " + poseName + " for untethered operation mode \t" + ", ".join([str(flt) for flt in servoValuesToBeSent]))
                    sendCommand("tup " + poseName + "\n")               
                
                if keypress == ord('+'):
                    # add a new pose
                    stdscr.addstr(3, 4, "enter name for new pose")
                    inputMode = "text"
                    textEntered = ""
                    textIntent = "pose"

            elif inputMode == "animation":
                # animation mode: toggle between animations and step through their poses
                

                if keypress == ord('p'):
                    inputMode = "pose"
                    
                if keypress == ord('e'):
                    inputMode = "animation_edit"
                    
                if keypress == ord('d'):
                    # remove animation, but ask before deleting
                    stdscr.addstr(3, 4, "delete animation " + animationName + " (y)?")
                    inputMode = "text"
                    textEntered = ""
                    textIntent = "animation_del"                    
                
                if keypress == ord('r'):
                    # rename animation
                    stdscr.addstr(3, 4, "rename animation " + animationName + ":")
                    inputMode = "text"
                    textEntered = ""
                    textIntent = "animation_rename"  
                    
                if keypress == ord('t'):
                    # transmit animation to be played
                    animationToBeSent = copy.deepcopy(animationDictionary[animationName])
                    storeSingleAnimation(animationName, animationToBeSent, poseDictionary) 
                    stdscr.addstr(3, 4, "transmit animation " + animationName + " for untethered operation mode: \t" + ", ".join(animationToBeSent))
                    sendCommand("tua " + animationName + "\n")  

                if keypress == 10:
                    # transmit and playback animation when hitting CR 
                    animationToBeSent = copy.deepcopy(animationDictionary[animationName])
                    storeSingleAnimation(animationName, animationToBeSent, poseDictionary)  
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
                    
                if keypress == ord('p'):
                    inputMode = "pose"
                
                if keypress == ord('a'):
                    inputMode = "animation"
                    
            else:
                stdscr.addstr(3, 4, "unknown inputMode")
                inputMode = "pose_edit"    
        
        # display ui in current mode
        
        if inputMode == "connect":
            
            ports = serial.tools.list_ports.comports()
            lineCounter = 5
            for p in ports:
                portToDisplay = lineCounter - 5
                if portToDisplay == currentPort:
                    stdscr.addstr(lineCounter, 4, str(portToDisplay) + ": " + p.device + " " + p.description, curses.A_REVERSE)
                else:
                    stdscr.addstr(lineCounter, 4, str(portToDisplay) + ": " + p.device + " " + p.description)
                lineCounter += 1    
            stdscr.addstr(2, 4, str(len(ports)) + " ports found")
            
        elif inputMode == "pose_edit":
            # control mode in pose, i.e. change the servo values for the current pose
            stdscr.addstr(2, 4, "edit mode for pose " + poseName)
            # print out overview
            stdscr.addstr(4, 4, "servos nubmers and their values:")

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
            stdscr.addstr(4, 4, "animation names and their poses:")
            
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


curses.wrapper(controlUI)

