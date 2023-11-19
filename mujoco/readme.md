this directory containing all the files for simulating Kayra in MuJoCo
the XML files refer via relative links to the STL files.

to install mujoco, just use pip install mujoco, see here for more details:
https://mujoco.readthedocs.io/en/stable/python.html

for exploring kayra's mujoco files, start the mujoco viewer using 
python3 -m mujoco.viewer and load one of the XML files

inspirations on learning how to build a robot in mujoco:
https://studywolf.wordpress.com/2020/03/22/building-models-in-mujoco/

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

