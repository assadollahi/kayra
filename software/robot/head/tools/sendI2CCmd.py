import machine
sda=machine.Pin(14) # ESP32
scl=machine.Pin(15) # ESP32
i2c=machine.I2C(0,sda=sda, scl=scl, freq=400000)
 
print('Scan i2c bus...')
devices = i2c.scan()
 
if len(devices) == 0:
  print("No i2c device !")
else:
  print('i2c devices found:',len(devices))
 
  for device in devices:  
    print("Decimal address: ",device," | Hex address: ",hex(device))
    
i2c.writeto(0x41, bytearray([12]))