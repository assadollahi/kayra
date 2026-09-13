# Wiring Kayra

How to get power and signals into the robot. This is a living document, it grows as
we build. Everything here refers to the Pimoroni Servo 2040 as the body controller.

> Work on the wiring with the battery disconnected. Connect the battery last, after
> you have checked the polarity of every connection.

## 1. Power

Kayra needs **two power rails**: a fat one for the servos and a small one for the
controller logic. They are separate on our boards, see the note below.

```
                 +--------------------+   servo voltage    +----------------+
  battery  --+-->|  UBEC / BEC  10 A  |------------------->| screw terminal |
             |   +--------------------+                    |  Servo 2040    |
             |                                             |                |
             |   +--------------------+   5 V              |  5V / GND pads |
             +-->|  small 5 V BEC     |------------------->|  (by Qwiic)    |
                 +--------------------+                    +----------------+
                                                   common ground everywhere
```

### The "Separate USB and Ext. Power" trace

On the back of the Servo 2040 there is a small trace labelled *Separate USB and
Ext. Power*, it looks like a dumb bell. From the factory it is **closed**, which ties
the screw terminal rail to the USB 5 V rail.

**On our board this trace is already cut.** That has two consequences:

- external power feeds the **servos only**, it can never push current back into the
  PC's USB port, and you may use servos above 5 V without damaging the RP2040
- the board gets **no logic power from the screw terminals**. It boots only from USB
  or from the 5 V / GND solder pads next to the Qwiic connector

So for **untethered operation** (USER button, no PC attached) you *must* feed 5 V into
those solder pads, otherwise the board simply stays dark. This is the single most
common reason for "the robot does nothing when I press the button".

### Sizing

- the Servo 2040 is not designed to distribute much more than **10 A**
- 18 servos at stall would be far more than that, but you never reach it in practice.
  A 10 A UBEC is a reasonable choice and usefully acts as a current limiter
- walking loads the servos much harder than standing, so do not size for idle current
- servo voltage: whatever the servos are rated for. The board supports up to 11 V now
  that the trace is cut. TODO: note the exact servos and voltage we settled on

## 2. Servo channels

The servo headers are numbered **1 to 18** on the silkscreen. The software counts
from **0**, so:

```
  board header 1  ==  software channel 0
  board header 18 ==  software channel 17
```

Which channel is which joint is defined in [`software/servoMap.json`](software/servoMap.json).
Short version, even = right, odd = left, bottom up per leg:

| channels | joints |
|----------|--------|
| 0, 1     | ankles R / L |
| 2, 3     | knees R / L |
| 4, 5     | hip pitch R / L |
| 6, 7     | hip yaw R / L |
| 8 .. 13  | arms, 3 per side (shoulder rotation, brace, elbow) |
| 14, 15   | unused |
| 16       | pelvis rotation |
| 17       | head pitch |

The arm and pelvis assignments are still marked `"verified": false` in the map. Confirm
them on the robot with:

```bash
python3 software/host/tools/identifyServo.py
```

Watch the silkscreen for the orientation of the three pin servo connectors, do not go by
cable colour alone.

## 3. IMU (BNO055)

Connected to **i2c0** at 400 kHz:

| BNO055 | Servo 2040 |
|--------|-----------|
| SDA    | GP20 |
| SCL    | GP21 |
| VIN    | 3V3 |
| GND    | GND |

Default address is `0x28`. To check that the board sees it, run
`software/robot/tools/i2cTest.py` on the controller, it scans the bus and prints every
address it finds.

## 4. USB to the host

USB-C from the Servo 2040 to the PC, 115200 baud. Used for:

- flashing and the Thonny REPL
- `software/host/interactiveServo.py`, the pose and animation editor
- `software/host/tools/identifyServo.py`
- the IMU readings the controller prints back to the host

`software/host/tools/serialPortInfo.py` lists the available ports if you are unsure
which one appeared.

## 5. Reading the LED bar

The controller reports its state on the WS2812 bar at boot:

| LED | green | red | blue |
|-----|-------|-----|------|
| 0 | `servoConfig.json` loaded | missing | |
| 1 | `servoControl.json` loaded | missing | |
| 2 | `servoMap.json` loaded | missing, **no servo limits are enforced** | |
| 5 | untethered mode | operation mode unknown | tethered mode |

A long press on the USER button in untethered mode switches back to tethered and turns
LED5 blue.

Copy all three JSON files to the board next to `main.py`.

## 6. Still to document

- the exact servos, their voltage and the battery we settle on
- battery mounting and the charging / swapping procedure
- ESP32 cam in the head, its I2C link to the body controller (currently out of scope)
- current and voltage sensing on the servo rail, the Servo 2040 can measure both and
  it would tell us about brownouts during walking
