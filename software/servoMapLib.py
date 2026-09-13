# shared loader for servoMap.json
#
# this is the single place where a servo channel number gets a meaning.
# used by:
#   host/interactiveServo.py        - names and limits in the pose editor
#   host/tools/identifyServo.py     - confirming the map on the real robot
#   mujoco/simulateAnimation.py     - servo channel -> MuJoCo actuator
#
# the servo controller firmware (robot/body/usbServosCluster.py) does NOT import
# this module, it reads servoMap.json directly, because on the servo2040 every
# extra file has to be copied to the board by hand.

import json
import os

DEFAULT_MAP_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "servoMap.json")


class ServoMap:

    def __init__(self, inMapDictionary):
        self.servos = inMapDictionary["servos"]
        self.servoCount = inMapDictionary["servoCount"]

        if len(self.servos) != self.servoCount:
            raise ValueError("servoMap.json: servoCount is " + str(self.servoCount) +
                             " but " + str(len(self.servos)) + " servos are defined")

        # channels have to be listed in order, everything downstream indexes into this list
        for expectedIndex, eachServo in enumerate(self.servos):
            if eachServo["index"] != expectedIndex:
                raise ValueError("servoMap.json: servo at position " + str(expectedIndex) +
                                 " has index " + str(eachServo["index"]))

        self.indexByName = {eachServo["name"]: eachServo["index"] for eachServo in self.servos}

    def servo(self, inServoNumber):
        return self.servos[inServoNumber]

    def name(self, inServoNumber):
        return self.servos[inServoNumber]["name"]

    def label(self, inServoNumber):
        return self.servos[inServoNumber]["label"]

    def index(self, inName):
        # look up a channel by its short name, e.g. index("kneeR") -> 2
        return self.indexByName[inName]

    def names(self):
        return [eachServo["name"] for eachServo in self.servos]

    def isEnabled(self, inServoNumber):
        return self.servos[inServoNumber]["enabled"]

    def limits(self, inServoNumber):
        eachServo = self.servos[inServoNumber]
        return (eachServo["min"], eachServo["max"])

    def clamp(self, inServoNumber, inServoValue):
        # keep a single servo inside its software limits
        eachServo = self.servos[inServoNumber]

        if not eachServo["enabled"]:
            return 0.0

        if inServoValue < eachServo["min"]:
            return eachServo["min"]
        if inServoValue > eachServo["max"]:
            return eachServo["max"]

        return inServoValue

    def clampAll(self, inServoValues):
        # keep a whole pose inside the software limits
        return [self.clamp(eachServoNumber, inServoValues[eachServoNumber])
                for eachServoNumber in range(len(inServoValues))]

    def isClamped(self, inServoNumber, inServoValue):
        # true when clamping would actually change the value, for warning the user
        return self.clamp(inServoNumber, inServoValue) != inServoValue

    def mujocoActuators(self):
        # [(servoNumber, actuatorName, sign), ...] for every channel the simulation knows
        outList = []
        for eachServo in self.servos:
            if eachServo["mujocoActuator"] is not None:
                outList.append((eachServo["index"], eachServo["mujocoActuator"], eachServo["mujocoSign"]))
        return outList

    def unverified(self):
        # channels whose joint assignment still has to be confirmed on the real robot
        return [eachServo["index"] for eachServo in self.servos if not eachServo["verified"]]

    def describe(self, inServoNumber):
        # one line summary, used by the UIs
        eachServo = self.servos[inServoNumber]
        outStr = eachServo["label"]

        if not eachServo["enabled"]:
            outStr += " (unused)"
        elif not eachServo["verified"]:
            outStr += " (?)"

        return outStr


def loadServoMap(inMapPath=None):
    if inMapPath is None:
        inMapPath = DEFAULT_MAP_PATH

    with open(inMapPath, "r") as f:
        inMapDictionary = json.load(f)

    return ServoMap(inMapDictionary)


def saveServoMap(inServoMap, inMapPath=None):
    # used by identifyServo.py to write back confirmed names and measured limits
    if inMapPath is None:
        inMapPath = DEFAULT_MAP_PATH

    # keep the comment block, it is the documentation of the file format
    with open(inMapPath, "r") as f:
        outDictionary = json.load(f)

    outDictionary["servos"] = inServoMap.servos

    with open(inMapPath, "w") as outfile:
        json.dump(outDictionary, outfile, indent=4)
