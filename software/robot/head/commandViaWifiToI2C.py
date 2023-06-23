import network
import socket
import sys
import machine

# connect to servo controller via I2C
sda=machine.Pin(14) # ESP32
scl=machine.Pin(15) # ESP32
i2c=machine.I2C(0,sda=sda, scl=scl, freq=400000)
 

# check Wifi status
wlan_sta = network.WLAN(network.STA_IF)
if wlan_sta.isconnected():
    print("wifi is connected")
    #print("IP details: " + str(station.ifconfig()))

# setup server
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "192.168.0.101" #"192.168.0.100"
port = 8000

# allow for re-use of addresses
serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# bind
serversocket.bind((host, port))

# listen
serversocket.listen(5)
print ("server started and listening at " + str(host) + ", port: " + str(port))

clientsocket, addr = serversocket.accept()
print("accepted connection from ", addr)
while True:
    rcvdData = clientsocket.recv(1024).decode()
    print("received: ",rcvdData)
    
    if(rcvdData == "exit"):
        clientsocket.send("shutting down".encode())
        break
    
    i2c.writeto(0x41, bytearray([int(rcvdData)]))
    
    '''
    sendData = input("send: ")
    clientsocket.send(sendData.encode())
    '''
    
print("closing connection")
clientsocket.close()
sys.exit()