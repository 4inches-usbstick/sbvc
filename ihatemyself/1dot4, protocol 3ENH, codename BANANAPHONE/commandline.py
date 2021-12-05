import socket
import cbedata

f = open('id.txt','r')
print('Your ID: '+f.read())
f.close()

f = open('config.cbedata','r')
inicfg = f.read()
f.close()

def netsetting(setting):
    global inicfg
    return cbedata.get_offline(inicfg, 'main-networking-'+str(setting), 'val')
    
UDP_IP = netsetting('remoteserver') #the remote server to push to (in this case, the same computer)
UDP_PORT = int(netsetting('udptalkingport')) #the port that the remote server listens to
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

print('Commands:\nCONNECT LOCAL_IP LISTEN_PORT CONNECTION_NAME DIAL_DESTIONATION\nDCONECT LOCAL_IP\n\nMake sure to have pull.py open for any output.')
while True:
    sock.sendto(bytes(input('$ '), 'utf-8'), (UDP_IP, UDP_PORT))
