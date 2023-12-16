import network
import socket
import sys

wlan_sta = network.WLAN(network.STA_IF)
if wlan_sta.isconnected():
    print("wifi is connected")
    print("IP details: " + str(station.ifconfig()))

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "192.168.0.100" #"192.168.0.100"
port = 8000

# allow for re-use of addresses
serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# bind
serversocket.bind((host, port))

'''
class client(Thread):
    def __init__(self, socket, address):
        Thread.__init__(self)
        self.sock = socket
        self.addr = address
        self.start()

    def run(self):
        while 1:
            print('Client sent:', self.sock.recv(1024).decode())
            self.sock.send(b'Oi you sent something to me')
'''
# listen
serversocket.listen(5)
print ("server started and listening at " + str(host) + ", port: " + str(port))

'''
while 1:
    clientsocket, address = serversocket.accept()
    #client(clientsocket, address)
    print("got connection from :", str(address))
    clientsocket.send("connection established")
'''

clientsocket, addr = serversocket.accept()
print("accepted connection from ", addr)
while True:
    rcvdData = clientsocket.recv(1024).decode()
    print("received: ",rcvdData)
    
    if(rcvdData == "exit"):
        clientsocket.send("shutting down".encode())
        break
    
    sendData = input("send: ")
    clientsocket.send(sendData.encode())

print("closing connection")
clientsocket.close()
sys.exit()