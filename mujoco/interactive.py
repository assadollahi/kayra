import time

import mujoco
import mujoco.viewer

global angle

def key_callback(keycode):
  global angle
  if chr(keycode) == '1':
    angle += 0.1


m = mujoco.MjModel.from_xml_path('./kayraCircle.xml')
d = mujoco.MjData(m)
angle = 0

#with mujoco.viewer.launch_passive(m, d) as viewer:
with mujoco.viewer.launch_passive(m, d, key_callback=key_callback) as viewer:
  viewer.opt.flags[mujoco.mjtVisFlag.mjVIS_CONTACTPOINT] = True

  start = time.time()

  while viewer.is_running():
    step_start = time.time()

    # mj_step can be replaced with code that also evaluates
    # a policy and applies a control signal before stepping the physics.
    mujoco.mj_step(m, d)

    # Example modification of a viewer option: toggle contact points every two seconds.
    with viewer.lock():
       
      d.actuator("Right Calf 3BR").ctrl = 1.57 - angle

    # Pick up changes to the physics state, apply perturbations, update options from GUI.
    viewer.sync()

    # Rudimentary time keeping, will drift relative to wall clock.
    time_until_next_step = m.opt.timestep - (time.time() - step_start)
    if time_until_next_step > 0:
      time.sleep(time_until_next_step)
