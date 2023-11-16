import socket
import struct
import time

config = open('app/utils/config.txt')

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

IP = socket.gethostbyname(socket.gethostname())
PORT = int(config.readline().strip(' PORT= \n'))

print('WAITING FOR CONNECTION') 

while True:
    
    try:
        client.connect((IP, PORT))
        print('CONNECTED')
        break
    except:
        time.sleep(1)

while True:    
    
    feedback=client.recv(36)

    for i in range(0, len(feedback), 12):
        print(struct.unpack('>fff', feedback[i:i + 12]))

    time.sleep(1)

    try:
        client.send(feedback)
    except:
        break

client.close()