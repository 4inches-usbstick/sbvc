import socket
import pyaudio
import wave
import os
import audioop
import threading
def fileget(file):
    f = open(file, 'rb')
    s = f.read()
    f.close()
    return s

#open audio interface
pp = pyaudio.PyAudio()
stream = pp.open(format=pyaudio.paInt16,channels=1,rate=44100,frames_per_buffer=1024,input=True)
info = pp.get_host_api_info_by_index(0)
numdevices = info.get('deviceCount')
print('\nLocated these audio inputs, choose one: \n\nID    Device\n---------------------------------------')
for i in range(0, numdevices):
        if (pp.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            print(i, " - ", pp.get_device_info_by_host_api_device_index(0, i).get('name'))
print('---------------------------------------\n')
pp.terminate()
pp = pyaudio.PyAudio()
stream = pp.open(format=pyaudio.paInt16,channels=1,rate=44100,frames_per_buffer=1024,input=True, input_device_index=int(input('Which mic? ')))


#open UDP interface
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) 

def push():
        sock.sendto(b'addip;127.0.0.1')
        while True:
            currentaudio = []
            for i in range(0, int(44100 / 1024 * float(0.1))):
                data = stream.read(1024)
                currentaudio.append(data)

            wf = wave.open('tmp.wav', 'wb')
            wf.setnchannels(1)
            wf.setsampwidth(pp.get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b''.join(currentaudio))
            wf.close()
            MESSAGE = fileget('tmp.wav')
            rms = audioop.rms(MESSAGE,1)
            print('Packet audio power: '+str(rms), end=', packet length: '+str(len(MESSAGE))+',\n')

            sock.sendto(b'push;C1;'+MESSAGE, ('127.0.0.1', 65431) )
            sock.sendto(b'read;C1', ('127.0.0.1', 65431) )

def pull():
        while True:
                print('Incoming packet:')
                ssock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
                ssock.bind(('',65432))
                data, addr = ssock.recvfrom(60000)
                if data:
                        print(len(data), data[0:10])
                

thread_push = threading.Thread(target=push)
thread_pull = threading.Thread(target=pull)

thread_push.start()
thread_pull.start()
