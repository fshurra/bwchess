#import multiprocessing as mp
import threading as mp
import Queue as q
from time import sleep
from udpnetwork import NetworkUDP
from serverclass import Serverissue as scmd
# the message list of the whole routine

# the udpSocket receiving
def listening(queue,ADDR_LISTEN):
    net = NetworkUDP(ADDR_LISTEN)
    while True:
        msgdata, remote_addr = net.listening()
        print "GOT:",msgdata
        msgdata = msgdata.split('|')
        if msgdata[-1] == '#':
            msgdata.append(remote_addr)
            queue.put(msgdata)
        if msgdata[-1] == '@':
            break
    return 
# the udpSocket sending
def sending(queue,ADDR_SENDING):
    net = NetworkUDP(ADDR_SENDING)
    while True:
        msg = queue.get()
        #print "sending ",msg
        if net.sending(msg[0], msg[1])==False:
            print "send",msg,"failed"
        print "Send Success",msg
        if msg[0][0] == '@':
            break
    return 
# and starting the server
def starting(queue,ADDR_LISTEN,ADDR_SENDING,ROOM_NUM,sendingqueue,listenqueue):
    #ROOM SETTIGN
    playerlist = []
    gameinfo = []
    n = 0
    #Starting the server
    cmd = scmd(ADDR_LISTEN,ADDR_SENDING,ROOM_NUM,playerlist,gameinfo,sendingqueue,listenqueue,n)
    print "Server Starting Success"
    while True:
        sleep(0.03)
        cmd.n += 1
        if queue.empty() == False:
            command = queue.get()
            command = command.split()
            #print command
            if command[0] in cmd.local_cmd:
                #print command[0]
                try:
                    ret = cmd.local_cmd[command[0]](command,0)
                except:
                    print "Invalid Command"
                    
                if ret == '@':
                    break
            else:
                #print 'Not in'
                print "Invalid Command"
            
        if listenqueue.empty() == False:
            msg = listenqueue.get()
            # msg ==> list(msg) ==> msg.append(remote_addr)
            cmd.server_cmd[msg[0]](msg,0)
        cmd.everygame()    
    return 0
# this will be the UI of the server
if __name__ == "__main__":
    print "Init the server starting"
    #starting Server issues
    ADDRESS = '127.0.0.1'
    PORT_LISTEN = 35000
    PORT_SEND = 35001
    ADDR_LISTEN = (ADDRESS,PORT_LISTEN)
    ADDR_SENDING = (ADDRESS,PORT_SEND)
    ROOM_NUM = 10
    commandqueue = q.Queue(10)
    sendingqueue = q.Queue(50)
    listenqueue = q.Queue(60)
    s = mp.Thread(target = starting, args = (commandqueue,ADDR_LISTEN,ADDR_SENDING,ROOM_NUM,sendingqueue,listenqueue))
    listenP = mp.Thread(target = listening, args = (listenqueue, ADDR_LISTEN))
    sendingP = mp.Thread(target = sending, args = (sendingqueue, ADDR_SENDING))
    #print local_cmd
    s.start()
    listenP.start()
    sendingP.start()
    while True:
        sleep(2)
        command = raw_input(">>>")
        commandqueue.put(command)
        if command == 'stop':
            sendingqueue.put(("@",ADDR_LISTEN))
            break
    listenP.join()
    sendingP.join()
    s.join()
    print 'Listening Thread Alive?',listenP.is_alive()
    print "Sending Thread Alive?",sendingP.is_alive()
    print 'Server Alive?',s.is_alive()
    print "The Server Stopped"
        
        
        