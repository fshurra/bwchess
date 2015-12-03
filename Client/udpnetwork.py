from socket import *
from time import sleep
BUFFER = 4096
RETRY = 1
TIMEOUT = 4
class NetworkUDP:
    def __init__(self,ADDR):
        self.sock = socket(AF_INET,SOCK_DGRAM)
        self.sock.bind(ADDR)
    
    def listening(self):
        msg, remote_addr = self.sock.recvfrom(4096)
        self.sock.sendto(msg, remote_addr)
        return msg, remote_addr
    
    def sending(self,msg,remote_addr):
        self.sock.settimeout(TIMEOUT)
        n = 0
        while n<RETRY:
            self.sock.sendto(msg, remote_addr)
            try:
                a = self.sock.recvfrom(4096)
            except error:
                n += 1
                print 'Sending',msg,remote_addr,"Timeout",n
                continue
            return True
        return False
    