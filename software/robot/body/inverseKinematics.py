import math

# all this is taken from the wonderful tutorial:
# https://dream-drive.net/robot/asi.htm

a: float = 10.0 # shin length

# XYZ coordinate system where the origin is at the waist, 
# the downward direction is the Z direction, 
# side is Y direction
# and the front is the X direction

# we want to move the foot along the axes:
x: float = 2.0 # move forward
y: float = 0.0 # move to the side
z: float = 2.0 # move down

l: float = math.sqrt(x**2 + y**2 + z**2) # distance hip to ankle
print(f'hip height l is: {l:.2f}')

delta: float = math.asin(x/l)
epsilon = math.atan(y/z)
alpha = math.acos(l/(2*a))
beta = math.asin(l/(2*a))

phi1 = alpha+delta # hip forward angle
phi2 = 2*beta # knee angle
phi3 = alpha - delta # ankle forward angle
phi45 = epsilon # hip / ankle sidewards angle

print(f'phi1: {phi1:.2f}')
print(f'phi2: {phi2:.2f}')
print(f'phi3: {phi3:.2f}')
print(f'phi45: {phi45:.2f}')