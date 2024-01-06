
MuJoCo simulation of Kayra 

some older work in progress, uses keyboard input to move the simulated ankle servo:
[![Alt text](https://img.youtube.com/vi/gwr96h01eZE/0.jpg)](https://youtube.com/shorts/gwr96h01eZE)

this directory containing all the files for simulating Kayra in MuJoCo
the XML files refer via relative links to the STL files.

to install mujoco, just use pip3 install mujoco, see here for more details:
https://mujoco.readthedocs.io/en/stable/python.html

for exploring kayra's mujoco files (*.xml), start the MuJoCo viewer using 
python3 -m mujoco.viewer and load one of the XML files

assuming that you have cloned kayra's git repo to home, you can also call the viewer with a file
python3 -m mujoco.viewer --mjcf=~/kayra/mujoco/kayraLowerBody.xml

for working with plots and animations you need:
apt update && apt install -y ffmpeg
pip install -q mediapy

**tutorial how to build Kayra in MuJoCo:**
https://kayra.org/mujoco-simulating-kayra/

humanoid robots are usually built by defining the body as a trunk
of a tree then adding four limbs to the body: 
- upper arms, lowe arms, hands
- upper legs, lower legs, feet
- optionally a head

kayra is special as many limbs (esp the feet) consist of four parts,
e.g. knee, front part (shin), back part (calf) and foot joint.

this constitutes a circle and has to be reflected in the definition 
of the robot in the mujoco XML

a working example for such circles was found here
https://github.com/deepmind/mujoco/issues/172

it's the file fourBars.xml in kayra's mujoco dir, i've added gravity
so that you can see that the loops behaves mechanically correctly.

the corresponding kayra file is kayraCircle.xml, it connects:
- 4R_Link (knee) to
- 3BR_Link (calf, back part, containing the servo / actuator) to
- 2R_Link (foot joint / ankle) to
- 3FU_Link (shin, front part of the leg)

further reading:
inspirations on learning how to build a robot in mujoco:
https://studywolf.wordpress.com/2020/03/22/building-models-in-mujoco/


