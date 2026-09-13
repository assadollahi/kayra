import time
import json
import copy
import math
import os
import sys
import mujoco
import mujoco.viewer

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "software"))
from servoMapLib import loadServoMap

# which servo channel drives which MuJoCo actuator
servoMap = loadServoMap()

# the channels that kayraLowerBody.xml actually models, as (servoNumber, actuator, sign)
mujocoActuatorList = servoMap.mujocoActuators()

# this is taken from kayra/softwre/host/interactiveServo.py
# servos
servoNumber = 0 # current servo to be controlled
servoValues = [0.0] * servoMap.servoCount # storing all servo values
servoStep = 10 # moving servo by this angle on key press

# poses
poseName = "neutral" # name of the current pose
poseHighlighted = "" # for editing animations
poseNumber = 0
poseDictionary = {} # dictionary of posture names and their servoValues
poseDictionary[poseName] = copy.deepcopy(servoValues)

# animation
animationName = "first"
animationStep = 0
animationPlaying = False
animationDictionary = {}
animationDictionary.update({animationName : [poseName]}) # first animation consists of the neutral pose only


global angle

def key_callback(keycode):
  global angle
  if chr(keycode) == '1':
    angle += 0.1

def setAllServos(inServoValues, inMjData):
  # drive every simulated joint straight from the servo map, so the channel
  # numbering and the sign convention only exist in servoMap.json
  for eachServoNumber, eachActuatorName, eachSign in mujocoActuatorList:
    servoValue = servoMap.clamp(eachServoNumber, inServoValues[eachServoNumber])
    inMjData.actuator(eachActuatorName).ctrl = math.radians(eachSign * servoValue)


def loadServoControl():
  global servoNumber, servoValues, servoStep
  global poseDictionary, poseName, poseHighlighted, poseNumber
  global animationNumber, animationName, animationDictionary, animationStep

  controlPath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "..", "software", "host", "servoControl.json")
  with open(controlPath, 'r') as f:
    inDictionary = json.load(f)	

  animationDictionary = copy.deepcopy(inDictionary["animations"])
  poseDictionary = copy.deepcopy(inDictionary["poses"])

  # go into neutral pose after loading poses    
  servoValues = copy.deepcopy(poseDictionary["crouch"])


m = mujoco.MjModel.from_xml_path('./kayraLowerBody.xml')
d = mujoco.MjData(m)
angle = 0

loadServoControl()
#setAllServos(servoValues, d)

#with mujoco.viewer.launch_passive(m, d) as viewer:
with mujoco.viewer.launch_passive(m, d, key_callback=key_callback) as viewer:
  #viewer.opt.flags[mujoco.mjtVisFlag.mjVIS_CONTACTPOINT] = True

  start = time.time()

  while viewer.is_running():
    step_start = time.time()

    # mj_step can be replaced with code that also evaluates
    # a policy and applies a control signal before stepping the physics.
    mujoco.mj_step(m, d)

    # Example modification of a viewer option: toggle contact points every two seconds.
    with viewer.lock():
      if(int(d.time%2) == 0):
        servoValues = copy.deepcopy(poseDictionary["neutral"])
      else:
        servoValues = copy.deepcopy(poseDictionary["crouch"])
      setAllServos(servoValues, d)
      

    # Pick up changes to the physics state, apply perturbations, update options from GUI.
    viewer.sync()

    # Rudimentary time keeping, will drift relative to wall clock.
    time_until_next_step = m.opt.timestep - (time.time() - step_start)
    if time_until_next_step > 0:
      time.sleep(time_until_next_step)
