import socket
import helpers
import cbedata
import sys
import os

allowedtospeakid = []

def ins(thing, lis):
    for i in lis:
        if thing == i:
            return True
    return False

print('The following arguments were passed to vcserver.py: '+str(sys.argv))


def fileget(file):
    f = open(file, 'r')
    s = f.read()
    f.close()
    return s

def netsetting(setting):
    global inicfg
    return cbedata.get_offline(inicfg, 'main-networking-'+str(setting), 'val')

inicfg = fileget('config.cbedata')

if len(sys.argv) == 1:
    mode0 = netsetting('channels')
else:
    mode0 = sys.argv[1]

try:
    UDP_IP = ''
    UDP_PORT = int(netsetting('listento'))
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
    sock.bind((UDP_IP, UDP_PORT))
except OSError:
    print('<Error> Another entity (external program or another instance of this application) is using port '+str(UDP_PORT)+', unable to initalize this relay.')
    input('[ENTER] to exit.')
    exit()

#initialize connections index
connections = {}

#testsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#testsock.bind( ('127.0.0.1', 1711) )

class Connection:
    def __init__(self, ip, port, metadata = {}):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ipaddress = ip
        self.portno = int(port)
        self.meta = metadata
        #self.sock.bind( (self.ipaddress,self.portno) )
        print(self.ipaddress,self.portno,':','Opened connection', end=', ')
        #self.sock.sendto(b'Request to connect accepted.', (self.ipaddress, self.portno) )
        print('sending back response on ports',netsetting('listento'),self.portno)
        #time.sleep(0.1)
        self.sock.sendto(b'AcceptedConnection', (self.ipaddress, int(netsetting('listento'))) )
    def transmit(self, data):
        self.sock.sendto(data, (self.ipaddress, self.portno) )
        print(self.ipaddress,self.portno,':','Relayed',len(data),'bytes')
    def close(self):
        self.sock.sendto(b'ClosedConnection', (self.ipaddress, self.portno))
        self.sock.close()
        print(self.ipaddress,self.portno,':','Closed down connection.')
    def info(self):
        print('This connection is tied to',self.ipaddress,'on port',self.portno)
        print('Connection metadata stored in memory: ',self.meta,'\n')
        

fss = helpers.filegeta('ips.txt').split('\n')
for i in fss:
    if i:
        iss = i.split(':')
        if mode0 == 'SINGLE':
            print('Creating a connection with',iss,'(from ips.txt)')
            connections[i] = Connection(iss[0], int(iss[1]))
            connections[i].info()
        if mode0 != 'SINGLE':
            print('Creating a connection with',iss,'(from ips.txt)')
            connections[i] = Connection(iss[0], int(iss[1]), {'dialto': iss[2]})
            connections[i].info()
        
print('\nSettings: PORT =',UDP_PORT,', PREDEFINED CONNECTIONS =',len(connections),', CHANNELMODE =',mode0)
os.system('title '+str(UDP_PORT)+' Relay')
print('Relay has fully initialized.\n')

if mode0 == 'SINGLE': #there is no reason to start in legacy mode
    print('<Error> Starting in legacy mode (SINGLE CHANNELMODE) is prohibited.')
    input('[ENTER] to exit.')
    exit()
    #while True:
        #data, addr = sock.recvfrom(60000) 
        #datstr = str(data)
        #relay = True
        #print('Incoming packet, first initials: '+str(data[0:10])+'')
        #if 'CONNECT' in datstr:
            #dats = helpers.debyte(datstr).split(' ')
            #connections[dats[3]] = Connection(dats[1], int(dats[2]))
            #print('>> CONNECT command issued, opened connection to',dats[1],'port',dats[2],', connection-name:',dats[3])
            #relay = False
            #connections[dats[3]].info()
        #if 'DCONECT' in datstr:
            #dats = helpers.debyte(datstr).split(' ')
            #connections[dats[3]].close()
            #print('>> DISCONNECT command issued, closing connection: '+dats[3])
            #del connections[dats[3]]
            #relay = False
        
        #if relay:
            #for key in connections:
                #connections[key].transmit(data)
                #mtestsock.sendto(data, ('127.0.0.1', 1711) )
if mode0 == 'MULTIPLE_LEGACYSTRICT':
    while True:
        data, addr = sock.recvfrom(60000) 
        datstr = str(data)
        relay = True
        #print('Incoming packet, first initials: '+str(data[0:10])+'')
        if 'CONNECT' in datstr:
            dats = helpers.debyte(datstr).split(' ')
            try:
                connections[dats[3]] = Connection(dats[1], int(dats[2]), {'dialto': str(dats[4])} )
                print('>> CONNECT command issued, opened connection to',dats[1],'port',dats[2],', connection-name:',dats[3],', dialed:',dats[4])
                relay = False
                connections[dats[3]].info()
            except:
                print('Invalid CONNECT command params, failed to connect.')
        if 'DCONECT' in datstr:
            dats = helpers.debyte(datstr).split(' ')
            try:
                connections[dats[1]].close()
            except:
                print('KeyError: the connection that the client has sent an ID of which is invalid.')
            print('>> DISCONNECT command issued, closing connection with ID: '+dats[1])
            del connections[dats[1]]
            relay = False
        if len(data) < 250:
            print('Nonaudio packet:',data)
        if relay:
            print("Packet from: "+str(data[0:8]).replace("b'", "").replace("'", ""))
            for key in connections:
                #datstrlist = datstr.split(':')
                #print(str(connections[key].meta['dialto']))
                #print(str(data[0:8]).replace("b'", "").replace("'", ""))
                if str(data[9-1:12]).replace("b'", "").replace("'", "") == str(key) and netsetting('selfreflect') == 'NO':
                        print('RelayError/CannotRelayToSelf from user: '+key)
                else:
                        connections[key].transmit(data)
                #only relay if the provided dialto is the same as the one the connection takes
if mode0 == 'SXS_PROXY':
    #this mode is mostly so people can have a firewall that shoots down unwanted connections
    sxs = helpers.filegeta('sxsproxyinfo.txt')
    sxsa = sxs.split('\n')
    print('<Info> Acting as proxy, relaying to: '+sxsa[0])
    os.system('title Proxy to '+sxsa[0])
    while True:
        data, addr = sock.recvfrom(60000)
        
if mode0 == 'MULTIPLE_OPENSTANDARD':
    while True:
        data, addr = sock.recvfrom(60000) 
        datstr = str(data)
        relay = True
        rancmd = False
        #print('Incoming packet, first initials: '+str(data[0:10])+'')
        myccmds = helpers.filegeta('custom.txt').split('[=]')
        
        for i in myccmds:
            if len(i) < 2:
                pass
            else:
                index0 = i.find('{')
                index1 = i.rfind('}')
                #print(i[index0+1:index1])
                exec(i[index0+1:index1])
        if rancmd:
            relay = False
        
        if relay:
            print("Packet from: "+str(data[0:8]).replace("b'", "").replace("'", ""))
            for key in connections:
                #datstrlist = datstr.split(':')
                #print(str(connections[key].meta['dialto']))
                #print(str(data[0:8]).replace("b'", "").replace("'", ""))
                if connections[key].meta['dialto'] == str(data[0:8]).replace("b'", "").replace("'", "") and 'NORELAY '+str(data[0:8]).replace("b'", "").replace("'", "") not in helpers.filegeta('acceptnoaccept.txt'): #CHANGE ADDR
                   # print('Checking '+key+' up against '+str(data[9-1:12]).replace("b'", "").replace("'", ""))
                   # print(str(key) == str(data[9-1:12]).replace("b'", "").replace("'", ""))
                    if str(data[9-1:12]).replace("b'", "").replace("'", "") == str(key) and netsetting('selfreflect') == 'NO':
                        print('RelayError/CannotRelayToSelf from user: '+key)
                    else:
                        connections[key].transmit(data)
                if 'NORELAY '+str(data[0:8]).replace("b'", "").replace("'", "") in helpers.filegeta('acceptnoaccept.txt'):
                    print('Policy has halted the relay from relaying any packets with destination: '+str(data[0:8]).replace("b'", "").replace("'", ""))
                    if netsetting('tellmewhymypacketswerenotrelayed') == 'YES':
                            connections[key].transmit(b'RelayError/CannotRelayToCertainAddr')
                #only relay if the provided dialto is the same as the one the connection takes
                


input('<Error> The relay is inactive because channel mode provided is invalid. [ENTER] to exit.')
