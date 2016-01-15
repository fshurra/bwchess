# List have 3 lists MSGDATA PLAYERLIST GAMEINFO SENDQUEUE
# The MSGDATA is like [COMMAND[,detail...],IDENTITY,remote_addr]
import json
import bwgame as bw

# Here are for Annotation usage
def unLogin(*args):
    print "You have to login first"
    return 0
def unRoom(*args):
    print "You have not join a room"
    return 0
def unPlaying(*args):
    print "You are not playing now"
    return 0

def checkLogin(func):
    def wrapper(*args,**kw):
        currentinfo = args[0].localgame.getinfo()
        #print args
        if currentinfo["Logined"]:
            return func(*args,**kw)
        else:
            return unLogin()
    return wrapper 

def checkPlaying(func):
    def wrapper(*args,**kw):
        currentinfo = args[0].localgame.getinfo()
        #print args
        if currentinfo["Playing"]:
            return func(*args,**kw)
        else:
            return unPlaying()
    return wrapper 

def checkRoom(func):
    def wrapper(*args,**kw):
        currentinfo = args[0].localgame.getinfo()
        #print args
        if currentinfo["Roomname"] != "":
            return func(*args,**kw)
        else:
            return unRoom()
    return wrapper 
    


class ClientGame(bw.BWGame):
    def __init__(self):
        bw.BWGame.__init__(self)
        self.mycolor = -1
        self.passcount = 0
        self.currentinfo = {
                            "Logined" : False,
                            "Roomname" : "",
                            "Playing" : False, 
                            "Id" : -1,
                            "Round" : 0
                            }
    
    def refreshinfo(self,*args):
        self.currentinfo["Logined"] = args[0]
        self.currentinfo["Roomname"] = args[1]
        self.currentinfo["Playing"] = args[2]
        self.currentinfo["Id"] = args[3]
        self.currentinfo["Round"] = self.count
    
    def getinfo(self):
        return self.currentinfo
    
    def checkCount(self,count):
        if count == self.count:
            return True
        else:
            return False
    
    def getcount(self):
        return self.count
    
    def getmycolor(self):
        return self.mycolor
    
    def setmycolor(self,color):
        self.mycolor = color
        
    def lput(self,x,y,color):
        if self.count%2 != self.mycolor:
            print "Not Your Turn"
            return False
        if bw.BWGame.put(self,x,y,color) == -1:
            return False
        return True
    
    def rput(self,x,y,color):
        if self.count%2 == self.mycolor:
            print "Sth Wrong Happened"
            return False
        bw.BWGame.put(self, x, y, color)
        return True
        
    def start(self):
        self.game_reset()
        self.count+=1
        
    def isPlaying(self):
        if self.count>0:
            return True
        else:
            return False
    
    def game_reset(self):
        self.game = [];
        for i in range(8):
            line = []
            for j in range(8):
                line.append(-1)
            self.game.append(line)
        self.mycolor = -1
        self.count = 0
        #need to add the chosing b/w here
        self.game[3][3] = 1
        self.game[4][4] = 1
        self.game[3][4] = 0
        self.game[4][3] = 0
        self.hist = []
        #print "reset Success"
        return 
    
    def OnEnd(self):
        me = 0
        oppo = 0
        for i in range(8):
            for j in range(8):
                if self.game[i][j] == -1:
                    continue
                if self.game[i][j] == int(self.mycolor):
                    me += 1
                else:
                    oppo += 1
        print "Your Point: ",me
        print "Oppo Point: ",oppo
        if me > oppo:
            print "You Win!"
            return True
        elif me == oppo:
            print "DRAW!"
            return False
        else:
            print "You Lose!"
            return False
    
    def needPass(self):
        # here check all -1
        n = 0
        for i in range(8):
            for j in range(8):
                if self.game[i][j] == -1:
                    if self.checkposition(i, j, self.mycolor) == -1:
                        n += 1
                else:
                    continue
        if n == 0:
            return True
        else:
            return False
        
class Clientissue:
    def notPlaying(self):
        if self.playing == False:
            print "Start a game First"
            return True
        return False
    def notInroom(self):
        if self.inroom == "":
            print "Join a game First"
            return True
        return False
    def notLogin(self):
        if self.logined == False:
            print "Login First"
            return True
        return False
        
    def __init__(self,ADDR_L,ADDR_S,sendingqueue,sendlock,game):
        self.ADDR_L = ADDR_L
        self.ADDR_S = ADDR_S
        self.sendingqueue = sendingqueue
        self.logined = False
        self.inroom = ""
        self.playing = False
        self.id = ''
        self.server_addr = ()
        self.sendlock = sendlock
        self.localgame = game
        #HERE ARE THE NETWORKCMDS
        self.client_cmd = {
                           "MSG": self.msg_receive,
                           "KO" : self.knocked_out,
                           "JSON": self.show_json,
                           "LOGIN" : self.receive_login,
                           "JOIN" :  self.receive_join,
                           "LEAVE": self.receive_leave,
                           "START" : self.receive_start,
                           "PUT": self.receive_put,
                           "PASS" : self.receive_pass,
                           "END" : self.receive_end
                           }
        #HERE ARE THE LOCALCMDS
        self.local_cmd = {
                           "stop" : self.stop_client,
                           "login" : self.client_login,
                           "logout" : self.client_logout,
                           "list" : self.client_list,
                           "games" : self.client_games,
                           "join" : self.client_join,
                           "leave" : self.client_leave,
                           "msg" : self.client_msg,
                           "retry":self.client_retry,
                           "put": self.client_put,
                           "pass":self.client_pass,
                           "reset-all":self.resetall
                          }

    #check all games every time
    def game_refreshinfo(self):
        self.localgame.refreshinfo(self.logined,self.inroom,self.playing,self.id)
    #game put pass end starts
    def receive_end(self,*args):
        self.localgame.OnEnd()
        msg = args[0]
        try:
            info = msg[1]
            if info == '1':
                self.playing = False
        except:
            return 
        return 
        
    def receive_pass(self,*args):
        msg = args[0]
        x = int(msg[1])
        y = int(msg[2])
        color = int(msg[3])
        roomname = msg[4]
        count = int(msg[5])
        #if self.localgame.checkCount(count) == False:
            #print "Wrong Leave Now"
            #self.client_leave()
            #return 0
        if self.localgame.rput(-1,-1,color):
            print "Round :",count,"PASS"
        if self.localgame.needPass():
            #print "PASS"
            self.client_pass([0,-1,-1,-1,-1])
            
            
    def receive_put(self,*args):
        msg = args[0]
        x = int(msg[1])
        y = int(msg[2])
        color = int(msg[3])
        roomname = msg[4]
        count = int(msg[5])
        #if self.localgame.checkCount(count) == False:
            #print "Wrong Leave Now"
            #self.client_leave()
            #return 0
        if self.localgame.rput(x,y,color):
            print "Round :",count,"POINT:",x,y,color
        if self.localgame.needPass():
            #print "PASS"
            self.client_pass([0,-1,-1,-1,-1])

    def client_pass(self,*args):
        msg = args[0]
        x = int(msg[1])
        y = int(msg[2])
        #color = int(msg[3])
        count = self.localgame.getcount()
        roomname = self.inroom
        if self.localgame.lput(-1,-1,self.localgame.getmycolor()):
            print "Round :",count,"PASS"
            self.send("PASS|"+"-1"+"|"+"-1"+"|"+str(self.localgame.getmycolor())+"|"+roomname+"|"+str(count)+"|#",self.server_addr)
        else:
            return 0
    @checkPlaying    
    def client_put(self,*args):
        msg = args[0]
        x = int(msg[1])
        y = int(msg[2])
        color = int(msg[3])
        count = self.localgame.getcount()
        roomname = self.inroom
        if self.localgame.lput(x,y,self.localgame.getmycolor()):
            print "Round :",count,x,y,self.localgame.getmycolor()
            self.send("PUT|"+str(x)+"|"+str(y)+"|"+str(self.localgame.getmycolor())+"|"+roomname+"|"+str(count)+"|#",self.server_addr)
        else:
            return 0
    
    #NET OPENRATION
    def receive_start(self,*args):
        msg = args[0]
        color = int(msg[2])
        self.localgame.start()
        self.localgame.setmycolor(color)
        self.playing = True
        print "Gamestart ","Colour:",color
        
    def receive_join(self,*args):
        msg = args[0]
        name = msg[1]
        print "Joined",name
        self.inroom = name
        return 0
    
    def receive_leave(self,*args):
        msg = args[0]
        print "Leaved",self.inroom
        self.inroom = ""
        self.playing = False
        return 0
    
    def receive_login(self,*args):
        msg = args[0]
        id = msg[1]
        self.id = id
        print "Get id:",id
        self.logined = True
        return 0
    
    def show_json(self,*args):
        msg = args[0]
        info = json.loads(msg[1])
        if len(info) == 0:
            print 'None'
            return 0
        for line in info:
            print line
        return 0
        
    def msg_receive(self,*args):
        msg = args[0]
        s = ''
        if msg[2] == "!":
            s = 'Server'
        else:
            s = msg[2]
        print "MSG_RECEIVED:",msg[1]," From:",s
        return 0
    
    def knocked_out(self,*args):
        msg = args[0]
        print msg[1]
        self.resetall()
        return 0
    
    #LOCAL OPERATION
    # login name ip port
    @checkPlaying
    def client_retry(self,*args):
        msg = args[0]
        self.send("RETRY|"+self.id+"|"+self.inroom+"|#",self.server_addr)
        return 0
    
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
    @checkLogin
    def client_logout(self,*args):
        msg = args[0]
        id = self.id
        if id == '':
            print 'You have not login'
        else:
            self.send("LOGOUT|"+id+"|#",self.server_addr)
            self.id = ''
            self.resetall()
        return 0
    
    @checkLogin
    def client_list(self,*args):
        print "Show the list:"
        self.send("LIST|#",self.server_addr)
        print "Name|Id"
        return 0
    
    @checkLogin
    def client_games(self,*args):
        print "Show the games:"
        self.send("GAMES|#",self.server_addr)
        print "[Roomname,[[Playerid(-1 = empty),status]]"
        return 0
        
    @checkLogin    
    def client_join(self,*args):
        msg = args[0]
        name = msg[1]
        self.send("JOIN|"+str(self.id)+"|"+name+"|#",self.server_addr)
        return 0
    @checkRoom
    def client_leave(self,*args):
        msg = args[0]
        #name = msg[1]
        self.send("LEAVE|"+str(self.id)+"|"+self.inroom+"|#",self.server_addr)
        #self.playing = False
        return 0
    # msg content d1,d2,d3
    @checkLogin
    def client_msg(self,*args):
        msg = args[0]
        content = ""
        dids = msg[-1]
        newmsg = msg[1:-1]
        for word in newmsg:
            content += word+" "
        sid = self.id
        message = "MSG|"+content+"|"+sid+"|"+dids+"|#"
        self.send(message,self.server_addr)
        
        return 0
    
    def stop_client(self,*args):
        print 'stopping client'
        #print self.sendingqueue
        #self.client_logout()
        #self.send("@",self.ADDR_L)
        return '@'
    
    def resetall(self,*args):
        self.logined = False
        self.inroom = ""
        self.playing = False
        self.id = ''
        self.server_addr = ()
        self.localgame.game_reset()
        
    def send(self,str,addr):
        msg = [str,addr]
        #print self.sendingqueue
        #print "Sending:",msg
        self.sendlock.acquire()
        self.sendingqueue.put(msg)
        self.sendlock.release()
        return 0