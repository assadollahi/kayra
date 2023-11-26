import time
import json
import copy
import math
import mujoco
import mujoco.viewer


# this is taken from kayra/softwre/host/interactiveServo.py
# servos
servoNumber = 0 # current servo to be controlled
servoValues = [0.0] * 18 # storing all servo values
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


global angle

def key_callback(keycode):
  global angle
  if chr(keycode) == '1':
    angle += 0.1

def setAllServos(inServoValues, inMjData):
  inMjData.actuator("Right Foot 1R").ctrl = math.radians(-inServoValues[0])
  inMjData.actuator("Left Foot 1L").ctrl = math.radians(-inServoValues[1])

  inMjData.actuator("Right Lower Calf 3BR" ).ctrl = math.radians(-inServoValues[2])
  inMjData.actuator("Left Lower Calf 3BL" ).ctrl = math.radians(-inServoValues[3])

  inMjData.actuator("Right Upper Calf 3BRU" ).ctrl = math.radians(-inServoValues[4])
  inMjData.actuator("Left Upper Calf 3BLU").ctrl = math.radians(-inServoValues[5])

  inMjData.actuator("Right Hip Joint 5R").ctrl = math.radians(-inServoValues[6])
  inMjData.actuator("Left Hip Joint 5L").ctrl = math.radians(-inServoValues[7])


def loadServoControl():
  global servoNumber, servoValues, servoStep
  global poseDictionary, poseName, poseHighlighted, poseNumber
  global animationNumber, animationName, animationDictionary, animationStep

  with open("../software/host/servoControl.json", 'r') as f:
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
