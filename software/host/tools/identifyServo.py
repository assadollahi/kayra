# this is intended to be run from a PC
#
# bench tool for confirming software/servoMap.json against the real robot.
#
# the servo map says which channel drives which joint. for the legs and the head
# that mapping is known, for the arms and the pelvis it is an educated guess
# (marked "verified": false in servoMap.json). this tool moves one channel at a
# time so you can watch Kayra and write down what actually moved.
#
# it can also record the mechanical limits of a joint: jog carefully towards a
# hard stop, back off a little, and store the value as min or max.
#
# the servo controller has to be in tethered mode (LED5 blue) and running
# usbServosCluster.py, exactly like for interactiveServo.py.
#
# SAFETY: this tool deliberately ignores the software limits in servoMap.json,
# otherwise you could never widen them. use step size 1 or 5 near a hard stop and
# stop as soon as the servo starts to buzz or the linkage binds.

import os
import sys
import time
import serial
import serial.tools.list_ports

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from servoMapLib import loadServoMap, saveServoMap

# the servo2040 cannot go beyond this, independent of the map
ABSOLUTE_LIMIT = 90.0

servoMap = loadServoMap()

serialPort = None
servoNumber = 0
servoValue = 0.0
servoStep = 5.0
mapChanged = False


def sendCommand(inCommand):
    serialPort.write((inCommand + "\n").encode('ASCII'))


def setSingleServo(inServoNumber, inServoValue):
    sendCommand("sss " + str(inServoNumber) + " " + str(inServoValue))


def connectToController():
    global serialPort

    ports = serial.tools.list_ports.comports()

    if len(ports) == 0:
        print("no serial ports found, is the controller plugged in?")
        return False

    print("available serial ports:")
    for portNumber, eachPort in enumerate(ports):
        print("  " + str(portNumber) + ": " + eachPort.device + " " + eachPort.description)

    enteredText = input("port number [0]: ").strip()
    portNumber = int(enteredText) if enteredText != "" else 0

    if portNumber < 0 or portNumber > (len(ports) - 1):
        print("no such port")
        return False

    serialPort = serial.Serial(ports[portNumber].device, 115200)
    print("connected to " + ports[portNumber].device)

    # give the controller a moment, it prints IMU lines continuously
    time.sleep(1.0)
    serialPort.reset_input_buffer()

    return True


def printServoList():
    print("")
    print("chan  name             joint                        min     max   status")
    for eachServoNumber in range(servoMap.servoCount):
        eachServo = servoMap.servo(eachServoNumber)

        status = ""
        if not eachServo["enabled"]:
            status = "unused"
        elif not eachServo["verified"]:
            status = "joint UNCONFIRMED"
        elif not eachServo["limitsVerified"]:
            status = "limits provisional"
        else:
            status = "ok"

        marker = ">" if eachServoNumber == servoNumber else " "

        print("{:1s}{:4d}  {:15s}  {:26s} {:6.1f}  {:6.1f}   {:s}".format(
            marker, eachServoNumber, eachServo["name"], eachServo["label"],
            eachServo["min"], eachServo["max"], status))
    print("")


def printHelp():
    print("""
commands:
  <number>   select channel 0..17 and drive it to 0 degrees
  l          list all channels
  +          jog the selected channel by +step
  -          jog the selected channel by -step
  s <deg>    set the step size, e.g. 's 1' near a hard stop
  g <deg>    go to an absolute angle
  z          go back to 0 degrees
  n <name>   rename the selected channel and mark its joint as confirmed
  min        store the current angle as the lower limit
  max        store the current angle as the upper limit
  w          write servoMap.json
  q          quit (servos stay where they are)
""")


def jogTo(inServoValue):
    global servoValue

    if inServoValue > ABSOLUTE_LIMIT:
        inServoValue = ABSOLUTE_LIMIT
        print("capped at +" + str(ABSOLUTE_LIMIT))
    if inServoValue < -ABSOLUTE_LIMIT:
        inServoValue = -ABSOLUTE_LIMIT
        print("capped at -" + str(ABSOLUTE_LIMIT))

    servoValue = inServoValue
    setSingleServo(servoNumber, servoValue)

    eachServo = servoMap.servo(servoNumber)
    outsideMap = servoValue < eachServo["min"] or servoValue > eachServo["max"]

    print("channel " + str(servoNumber) + " (" + eachServo["name"] + ") -> " +
          str(servoValue) + " deg" + ("   [outside the current map limits]" if outsideMap else ""))


def main():
    global servoNumber, servoValue, servoStep, mapChanged

    print("Kayra servo identification tool")
    print("the controller has to be in tethered mode (LED5 blue)")

    if not connectToController():
        return

    unverifiedList = servoMap.unverified()
    if len(unverifiedList) > 0:
        print("")
        print("channels with an unconfirmed joint assignment: " +
              ", ".join([str(eachServoNumber) + " (" + servoMap.name(eachServoNumber) + ")"
                         for eachServoNumber in unverifiedList]))

    printHelp()
    printServoList()

    while True:
        enteredText = input("servo " + str(servoNumber) + " @ " + str(servoValue) +
                            " deg, step " + str(servoStep) + " > ").strip()

        if enteredText == "":
            continue

        commandSplit = enteredText.split()
        cmdString = commandSplit[0]

        if cmdString == "q":
            if mapChanged:
                enteredText = input("servoMap.json has unsaved changes, write it now? [y/N] ").strip()
                if enteredText.lower() == "y":
                    saveServoMap(servoMap)
                    print("servoMap.json written")
            break

        elif cmdString == "l":
            printServoList()

        elif cmdString == "h" or cmdString == "?":
            printHelp()

        elif cmdString.isdigit():
            newServoNumber = int(cmdString)

            if newServoNumber < 0 or newServoNumber > (servoMap.servoCount - 1):
                print("channel has to be 0.." + str(servoMap.servoCount - 1))
                continue

            servoNumber = newServoNumber
            print("selected channel " + str(servoNumber) + ": " + servoMap.describe(servoNumber))
            jogTo(0.0)

        elif cmdString == "+":
            jogTo(servoValue + servoStep)

        elif cmdString == "-":
            jogTo(servoValue - servoStep)

        elif cmdString == "z":
            jogTo(0.0)

        elif cmdString == "s":
            if len(commandSplit) < 2:
                print("usage: s <degrees>")
                continue
            servoStep = float(commandSplit[1])
            print("step size is now " + str(servoStep))

        elif cmdString == "g":
            if len(commandSplit) < 2:
                print("usage: g <degrees>")
                continue
            jogTo(float(commandSplit[1]))

        elif cmdString == "n":
            if len(commandSplit) < 2:
                print("usage: n <name>, e.g. 'n shoulderRotR'")
                continue

            newName = commandSplit[1]
            eachServo = servoMap.servo(servoNumber)
            oldName = eachServo["name"]

            if newName in servoMap.indexByName and servoMap.indexByName[newName] != servoNumber:
                print("name " + newName + " is already used by channel " +
                      str(servoMap.indexByName[newName]))
                continue

            del servoMap.indexByName[oldName]
            eachServo["name"] = newName
            eachServo["verified"] = True
            servoMap.indexByName[newName] = servoNumber

            mapChanged = True
            print("channel " + str(servoNumber) + ": " + oldName + " -> " + newName +
                  ", joint marked as confirmed")

        elif cmdString == "min":
            eachServo = servoMap.servo(servoNumber)
            eachServo["min"] = servoValue

            if eachServo["max"] < servoValue:
                print("note: max (" + str(eachServo["max"]) + ") is below the new min, set max too")

            mapChanged = True
            print("channel " + str(servoNumber) + " min = " + str(servoValue))

        elif cmdString == "max":
            eachServo = servoMap.servo(servoNumber)
            eachServo["max"] = servoValue

            if eachServo["min"] > servoValue:
                print("note: min (" + str(eachServo["min"]) + ") is above the new max, set min too")

            # both limits touched by hand means they are no longer provisional
            eachServo["limitsVerified"] = True
            mapChanged = True
            print("channel " + str(servoNumber) + " max = " + str(servoValue) +
                  ", limits marked as measured")

        elif cmdString == "w":
            saveServoMap(servoMap)
            mapChanged = False
            print("servoMap.json written")

        else:
            print("unknown command: " + cmdString + ", try 'h'")

    if serialPort is not None:
        serialPort.close()

    print("done")


main()
