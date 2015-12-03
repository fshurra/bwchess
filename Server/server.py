import multiprocessing as mp
from time import sleep
from udpnetwork import NetworkUDP
import netcmdS as cmdS
# the message list of the whole routine

# the udpSocket receiving
def listening(queue,ADDR_LISTEN):
    net = NetworkUDP(ADDR_LISTEN)
    while True:
        msgdata, remote_addr = net.listening()
        msgdata = msgdata.split()
        if msgdata[-1] == '#':
            msgdata.append(remote_addr)
            queue.put(msgdata)
        if msgdata[-1] == '@':
            break
    
    return 0
# the udpSocket sending
def sending(queue,ADDR_SENDING):
    net = NetworkUDP(ADDR_SENDING)
    while True:
        msg = queue.get(block = True)
        if net.sending(msg[0], msg[1])==False:
            print "send",msg,"failed"
        if msg[0][0] == '@':
            break
    return 0
# and starting the server
def starting(queue):
    #NET WORK SETTING
    ADDRESS = '127.0.0.1'
    PORT_LISTEN = 35000
    PORT_SEND = 35001
    ADDR_LISTEN = (ADDRESS,PORT_LISTEN)
    ADDR_SENDING = (ADDRESS,PORT_SEND)
    #ROOM SETTIGN
    ROOM_NUM = 10
    ROOM_NUM += 1
    #INIT BASIC THINGS
    playerlist = []
    gameinfo = []
    n = 0
    sendingqueue = mp.Queue(20)
    listenqueue = mp.Queue(20)
    listenP = mp.Process(target = listening, args = (listenqueue, ADDR_LISTEN))
    sendingP = mp.Process(target = sending, args = (sendingqueue, ADDR_SENDING))
    #Starting the server
    listenP.start()
    sendingP.start()
    print "Server Starting Success"
    while True:
        sleep(0.1)
        n += 1
        if queue.empty() == False:
            command = queue.get()
            if command == 'stop':
                print 'stopping Server'
                sendingqueue.put(("@",ADDR_LISTEN))
                break
            elif command == 'show':
                print n
            else:
                print "Invalid Command"
        if listenqueue.empty() == False:
            msg = listenqueue.get()
            cmdS.server_cmd[msg[0][0]](msg,playerlist,gameinfo,sendingqueue)
            
            
    
    listenP.join()
    sendingP.join()
    print 'Listening Process Alive?',listenP.is_alive()
    print "Sending Process Alive?",sendingP.is_alive()
    return 0
# this will be the UI of the server
if __name__ == "__main__":
    print "Init the server starting"
    #starting Server issues
    commandqueue = mp.Queue(10)
    s = mp.Process(target = starting, args = (commandqueue,))
    s.start()
    while True:
        sleep(1)
        command = raw_input(">>>")
        commandqueue.put(command)
        if command == 'stop':
            break
    s.join()
    print 'Server Alive?',s.is_alive()
    print "The Server Stopped"
        
        
        