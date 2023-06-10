import machine
sda=machine.Pin(20) # Explorer 20 Breakout 4
scl=machine.Pin(21) # Explorer 21 Breakout 5
i2c=machine.I2C(0,sda=sda, scl=scl, freq=400000)
 
print('Scan i2c bus...')
devices = i2c.scan()
 
if len(devices) == 0:
  print("No i2c device !")
else:
  print('i2c devices found:',len(devices))
 
  for device in devices:  
    print("Decimal address: ",device," | Hex address: ",hex(device))