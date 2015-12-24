import threading as mp
import multiprocessing as q
from time import sleep
from udpnetwork import NetworkUDP
from clientclass import Clientissue as ccmd
import wx
import clientGUI as gui


def listening(queue,ADDR_LISTEN,lock):
    net = NetworkUDP(ADDR_LISTEN)
    while True:
        msgdata, remote_addr = net.listening()
        print "GOT:",msgdata
        msgdata = msgdata.split('|')
        if msgdata[-1] == '!':
            msgdata.append(remote_addr)
            lock.acquire()
            queue.put(msgdata)
            lock.release()
        if msgdata[-1] == '@':
            break
    return 
# the udpSocket sending
def sending(queue,ADDR_SENDING,lock):
    net = NetworkUDP(ADDR_SENDING)
    #print queue
    while True:
        #print 'this is sending'
        sleep(0.1)
        #print "sending Thread"
        if lock.acquire(1) == True:
            if queue.empty() == False:
                msg = queue.get()
                lock.release()
                #print "sending ",msg
                if net.sending(msg[0], msg[1]) == False:
                    print "send",msg,"failed"
                else:
                    print "Send Success",msg
                if msg[0][0] == '@':
                    break
            else:
                lock.release()
    return 

def starting(queue,ADDR_LISTEN,ADDR_SENDING,listenqueue,sendingqueue,commandLock,sendLock,listenLock,game):
    
    cmd = ccmd(ADDR_LISTEN,ADDR_SENDING,sendingqueue,sendLock,game)
    
    print sendingqueue
    while True:
        sleep(0.5)
        if commandLock.acquire(1) == True:
            if queue.empty() == False:
                command = queue.get()
                commandLock.release()
                command = command.split()
                if command[0] in cmd.local_cmd:
                    ret = ''
                #print command[0]
                    try:
                        ret = cmd.local_cmd[command[0]](command,0)
                    except Exception as e:
                        print e
                        print "Invalid Command"
                        
                    if ret == '@':
                        break
                else:
                    print "Invalid Command"
            else:
                commandLock.release()
            #print command
        if listenLock.acquire(1) == True:
            if listenqueue.empty() == False:
                msg = listenqueue.get()
                listenLock.release()
            # msg ==> list(msg) ==> msg.append(remote_addr)
                cmd.client_cmd[msg[0]](msg,0)
            else:
                listenLock.release()
        
    return 0


if __name__ == "__main__":
    ADDR = "127.0.0.1"
    LISTEN = 40000
    SEND = LISTEN + 1
    ADDR_LISTEN = (ADDR,LISTEN)
    ADDR_SENDING = (ADDR,SEND)
    sendingqueue = q.Queue(30)
    #print sendingqueue
    listenqueue = q.Queue(50)
    commandqueue = q.Queue(10)
    sendLock = mp.Lock()
    listenLock = mp.Lock()
    commandLock = mp.Lock()
    game = gui.ClientGame()
    listenP = mp.Thread(target = listening, args = (listenqueue, ADDR_LISTEN,listenLock))
    sendingP = mp.Thread(target = sending, args = (sendingqueue, ADDR_SENDING,sendLock))
    s = mp.Thread(target = starting, args = (commandqueue,ADDR_LISTEN,ADDR_SENDING,listenqueue,sendingqueue,commandLock,sendLock,listenLock,game))
    s.start()
    listenP.start()
    sendingP.start()
    #here is for console usage
    '''
    while True:
        sleep(1)
        command = raw_input(">>>")
        commandqueue.put(command)
        if command == 'stop':
            stopmsg = ["@",ADDR_LISTEN]
            sendLock.acquire()
            sendingqueue.put(stopmsg)
            sendLock.release()
            break
    '''
    
    app = gui.BWchessApp(commandqueue,game)
    print "Client Starting Success"
    app.MainLoop()
    
    commandqueue.put("stop")
    stopmsg = ["@",ADDR_LISTEN]
    sendLock.acquire()
    sendingqueue.put(stopmsg)
    sendLock.release()
    listenP.join()
    sendingP.join()
    s.join()
    print 'Listening Thread Alive?',listenP.is_alive()
    print "Sending Thread Alive?",sendingP.is_alive()
    print 'Client Alive?',s.is_alive()
    print "The Client Stopped"
    
    