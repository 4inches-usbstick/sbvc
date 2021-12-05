import socket, glob, time
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) 
sock.bind(('', 65431))

listofips = ['127.0.0.1']
dumpbufferticker = 0

def debyte(inp):
    inp = str(inp)
    return inp.replace("b'","").replace("'","")

while True:
    data, addr = sock.recvfrom(60000)
    reqcontents = debyte(data)
    
    reqcmd = reqcontents.split(';')[0]
    reqparams = reqcontents.split(';')
    bytereqparams = data.split(b';')
    iptolog = addr[0]
    
    #handle request
    if data:  
        if reqcmd == 'push':
            print('Push request:',reqparams)
            for i in listofips:
                try: sock.sendto(bytereqparams[2], (i,65432) )
                except: pass
    
        if reqcmd == 'addip':
            print('AddIp request:',reqparams)
            if reqparams[1] not in listofips:
                listofips.append(reqparams[1])

        if reqcmd == 'delip':
            print('DelIp request:',reqparams)
            try: listofips.remove(reqparams[1])
            except: pass
        
    #dump buffers after certain number of packets
    dumpbufferticker = dumpbufferticker + 1
    #print(dumpbufferticker)        
    if dumpbufferticker > 3:
        for i in glob.glob('*.buffer'):
            f = open(i, 'w')
            f.close()
            dumpbufferticker = 0
            
    
