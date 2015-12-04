# List have 3 lists MSGDATA PLAYERLIST GAMEINFO SENDQUEUE
# The MSGDATA is like [COMMAND[,detail...],IDENTITY,remote_addr]
import json

class Clientissue:
    def __init__(self,ADDR_L,ADDR_S,sendingqueue,sendlock):
        self.ADDR_L = ADDR_L
        self.ADDR_S = ADDR_S
        self.sendingqueue = sendingqueue
        self.logined = 0
        self.inroom = 0
        self.playing = 0
        self.id = ''
        self.server_addr = ()
        self.sendlock = sendlock
        #HERE ARE THE NETWORKCMDS
        self.client_cmd = {
                           "MSG": self.msg_receive,
                           "KO" : self.knocked_out,
                           "JSON": self.show_json,
                           "LOGIN" : self.receive_login
                           }
        #HERE ARE THE LOCALCMDS
        self.local_cmd = {
                           "stop" : self.stop_client,
                           "login" : self.client_login,
                           "logout" : self.client_logout,
                           "list" : self.client_list,
                           "games" : self.client_games,
                           "join" : self.client_join,
                           "msg" : self.client_msg
                          }

    #check all games every time
    
    #NET OPENRATION
    def receive_login(self,*args):
        msg = args[0]
        id = msg[1]
        self.id = id
        print "Get id:",id
        return 0
    
    def show_json(self,*args):
        msg = args[0]
        info = json.loads(msg[1])
        for line in info:
            print line
        return 0
        
    def msg_receive(self,*args):
        msg = args[0]
        print "MSG_RECEIVED:",msg[1]
        return 0
    
    def knocked_out(self,*args):
        self.inroom = 0
        msg = args[0]
        print msg[1]
        return 0
    
    #LOCAL OPERATION
    # login name ip port
    def client_login(self,*args):
        #print "run"
        msg = args[0]
        name = msg[1]
        ip = msg[2]
        port = msg[3]
        server_addr = (ip,int(port))
        print server_addr
        self.send("LOGIN|"+name+"|#",server_addr)
        self.server_addr = server_addr
        return 1
    
    def client_logout(self,*args):
        return 0
    
    def client_list(self,*args):
        
        return 0
        
    def client_games(self,*args):
        return 0
        
    def client_join(self,*args):
        return 0
    
    def client_msg(self):
        return 0
    
    def stop_client(self,*args):
        print 'stopping client'
        #print self.sendingqueue
        #self.client_logout()
        #self.send("@",self.ADDR_L)
        return '@'
    
    def send(self,str,addr):
        msg = [str,addr]
        print self.sendingqueue
        #print "Sending:",msg
        self.sendlock.acquire()
        self.sendingqueue.put = (msg)
        self.sendlock.release()
        return 0