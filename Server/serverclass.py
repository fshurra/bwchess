# List have 3 lists MSGDATA PLAYERLIST GAMEINFO SENDQUEUE
# The MSGDATA is like [COMMAND[,detail...],IDENTITY,remote_addr]
import json
import bwgame as bw
import random

def illegalCommand():
    print "Player not loggedin"
    return

def checkPlayerexist(func):
    def warpper(*args,**kw):
        clAss = args[0]
        msg = args[1]
        addr = msg[-1]
        print addr
        addr = list(addr)
        addr[1] = addr[1] -1
        addr = tuple(addr)
        info = clAss.playerexist(addr)
        if info == -1:
           #clAss.send("KO|!",addr)
            return illegalCommand()
        else:
            return func(*args,**kw)
    return warpper

class ServerGame(bw.BWGame):
    def __init__(self):
        bw.BWGame.__init__(self)
        self.serverplayer = [-1,-1]
        self.serverplayerinfo = {}
        self.retryflags = [0,0]
    
    def isDoublePass(self):
        a = self.hist[-1]
        b = self.hist[-2]
        if a[1] == -1 and b[1] == -1:
            return True
        else:
            return False
        
    def getoppoaddr(self,color):
        if color == 1:
            id = self.player[1][0]
            return self.serverplayerinfo[id][0]
        else:
            id = self.player[0][0]
            return self.serverplayerinfo[id][0]
    
    def addcount(self):
        self.count += 1
        
    def checkcount(self,count):
        if count != self.count:
            return False
        return True
    
    def record(self,his):
        self.hist.append(his)
        
    def isPlaying(self):
        if self.count > 0:
            return True
        else:
            return False
        
    def start(self,sender):
        self.count += 1
        for player in self.player:
            id = player[0]
            addr = self.serverplayerinfo[id][0]
            sender("START|"+str(player[0])+"|"+str(player[1])+"|!",addr)
        return 
    
    def game_reset(self):
        self.game = [];
        for i in range(8):
            line = []
            for j in range(8):
                line.append(-1)
            self.game.append(line)
        
        self.count = 0
        #need to add the chosing b/w here
        self.game[3][3] = 1
        self.game[4][4] = 1
        self.game[3][4] = 0
        self.game[4][3] = 0
        self.retryflags = [0,0]
        self.hist = []
        print "reset Success"
        return 
    
    def isFull(self):
        players = self.getserverplayer()
        for id in self.getserverplayer():
            if id == -1:
                return False
        return True
    
    
    def needRetry(self):
        if 0 not in self.retryflags:
            return True
        else:
            return False
        
    def setblackandwhite(self,id1,id0):
        self.player[0][0] = id1
        self.player[1][0] = id0
    
    def exchangeblackandwhite(self):
        tid = self.player[0][0]
        self.player[0][0] = self.player[0][1]
        self.player[0][1] = tid
        
    
    def setretryflag(self,id):
        for i in range(2):
            if self.serverplayer[i] == id:
                self.retryflags[i] = 1
        return True
    
    def join(self,id,playerinfo):
        if self.isFull():
            return False
        if id in self.serverplayer:
            return False
        for i in range(2):
            if self.serverplayer[i] == -1:
                self.serverplayer[i] = id
                self.serverplayerinfo[id] = playerinfo
                return True
            else:
                continue
        return False
    
    def exit(self,id,playerinfo):
        for i in range(2):
            if self.serverplayer[i] == id:
                self.serverplayer.pop(i)
                self.serverplayer.append(-1)
                del self.serverplayerinfo[id]
                return True
        return False
    
     
    def getround_now(self):
        return self.count
    
    def getinfo(self):
        if self.isPlaying():
            return [self.serverplayer,"playing"]
        else:
            return [self.serverplayer,"idle"]
    
    def getretryflag(self):
        return self.retryflags
    
    def getserverplayer(self):    
        return self.serverplayer
    
class Serverissue:
    def __init__(self,ADDR_L,ADDR_S,ROOM_NUM,playerlist,gameinfo,sendingqueue,listenqueue,n):
        self.ADDR_L = ADDR_L
        self.ADDR_S = ADDR_S
        self.playerlist = playerlist
        self.gameinfo = gameinfo
        self.sendingqueue = sendingqueue
        self.listenqueue = listenqueue
        self.ROOM_NUM = ROOM_NUM
        self.n = n
        self.id = []
        self.idtoinfo = {}
        #emptygame["name",[id1,id2],[color1,color2],[retry1,retry2],roundnow,[the list of operation]]
        #self.emptygame = ["NA",[-1,-1],[8,8],[0,0],0,[]]
        #HERE ARE THE NETWORKCMDS
        self.server_cmd = {
                           "LOGIN" : self.server_login,
                           "LOGOUT" : self.server_logout,
                           "LIST" : self.server_list,
                           "GAMES" : self.server_games,
                           "JOIN" : self.server_join,
                           "LEAVE": self.server_leave,
                           "MSG" : self.server_msg,
                           "RETRY" : self.server_retry,
                           
                           "PUT":self.server_put,
                           "PASS":self.server_pass,
                           #"CHOSE":self.server_chose
                           }
        #HERE ARE THE LOCALCMDS
        self.local_cmd = {
                           "stop" : self.stop_server,
                           "show" : self.show_n,
                           "test" : self.test,
                           "opengame" : self.opengame,
                           "closegame" : self.closegame,
                           "reset-all" : self.resetall,
                           'kick' : self.kickplayer,
                           "showgame" : self.showgame,
                           "disconnect" : self.disconnect
                          }
        #some default message to send
        self.errormsg = {
                         "PLAYER_FULL": "MSG|The Server is Full|!",
                         "KICKED_OUT": "KO|You have been kicked out|!",
                         "LOGIN_SUCCESS": "MSG|Login Success|!",
                         "LOGOUT_SUCCESS": "MSG|Logged Out|!",
                         "LOGINED" : 'MSG|You Have Already Login!|!'
                         }

    #game play info
    @checkPlayerexist
    def server_put(self,*args):
        msg = args[0]
        x = int(msg[1])
        y = int(msg[2])
        color = int(msg[3])
        count = int(msg[5])
        roomname = msg[4]
        index = self.gameexist(roomname)
        self.gameinfo[index][1].put(x,y,color)
        self.gameinfo[index][1].addcount()
        msg[-1] = "!"
        msg = "|".join(msg)
        self.send(msg,self.gameinfo[index][1].getoppoaddr(color))
        return 0
    @checkPlayerexist    
    def server_pass(self,*args):
        msg = args[0]
        x = int(msg[1])
        y = int(msg[2])
        color = int(msg[3])
        count = int(msg[5])
        roomname = msg[4]
        index = self.gameexist(roomname)
        self.gameinfo[index][1].put(-1,-1,color)
        self.gameinfo[index][1].addcount()
        msg[-1] = "!"
        msg = "|".join(msg)
        if self.gameinfo[index][1].isDoublePass():
            for id in self.gameinfo[index][1].getserverplayer():
                addr = self.idtoinfo[id][0]
                self.send("END|!",addr)
        else:
            self.send(msg,self.gameinfo[index][1].getoppoaddr(color))
        return 0
        
    #check all games every time
    def randomselect(self,players):
        a = random.randint(0,100)
        b = random.randint(0,100)
        addr0 = self.idtoinfo[players[0]][0]
        addr1 = self.idtoinfo[players[1]][0]
        self.send("MSG|"+players[0]+" rolls:"+str(a)+" and "+players[1]+" rolls:"+str(b)+"|!", addr0)
        self.send("MSG|"+players[0]+" rolls:"+str(a)+" and "+players[1]+" rolls:"+str(b)+"|!", addr1)
        if a>=b:
            id1 = players[0]
            id0 = players[1]
        else:
            id0 = players[0]
            id1 = players[1]            
        return id1,id0
    
    def everygame(self):
        #check if full
        for game in self.gameinfo:
            name = game[0]
            game = game[1]
            if game.isFull():
                if game.isPlaying():
                    #check retry flag
                    if game.needRetry():
                        players = game.getserverplayer()
                        id1,id0 = self.randomselect(players)
                        game.setblackandwhite(id1,id0)
                        game.game_reset()
                        game.start(self.send)        
                else:
                    #do the selection
                    players = game.getserverplayer()
                    id1,id0 = self.randomselect(players)
                    game.setblackandwhite(id1,id0)
                    #start the game
                    game.start(self.send)
            if game.isFull() == False:
                #some one exit
                if game.isPlaying():
                    for player in game.getserverplayer():
                        if player != -1:
                            try:
                                addr = self.idtoinfo[player][0]
                                self.send("MSG|The another player has left!|!", addr)
                                self.send("END|1|!",addr)
                            except Exception as e:
                                print e
                            
                    game.game_reset()    
        
        return
    
    #NETWORK FUNC
    @checkPlayerexist
    def server_retry(self,*args):
        msg = args[0]
        id = msg[1]
        addr = self.idtoinfo[id][0]
        roomname = msg[2]
        #if self.gameexist(roomname) == -1:
        roomnum = self.gameexist(roomname)
        if roomnum == -1:
            self.send("MSG|No such Room"+roomname+"|!",addr)
        else:
            self.gameinfo[roomnum][1].setretryflag(id)
            for players in self.gameinfo[roomnum][1].getserverplayer():
                taddr = self.idtoinfo[players][0]
                self.send("MSG|Player "+str(id)+" want to retry|!",taddr)
        return 0
        

    
    def server_login(self,*args):
        msg = args[0]
        player = []
        addr = msg[-1]
        # change the addr of client to theres listening port
        addr = list(addr)
        addr[1] = addr[1] - 1
        addr = tuple(addr)
        name = msg[1]
        oid = self.playerexist(addr)
        if oid != -1:
            self.send(self.errormsg['LOGINED'],addr)
            self.send("LOGIN|"+oid+'|!',addr)
            return 0
        id = self.getid()
        if id == -1:
            self.send(self.errormsg["PLAYER_FULL"],addr)
            print "PLAYER_FULL"
        self.idtoinfo[id] = [addr,name,"IDLE"]
        self.id.append(id)
        #print 'login',player
        self.send(self.errormsg["LOGIN_SUCCESS"],addr)
        self.send("LOGIN|"+id+'|!',addr)
        #print self.errormsg["LOGIN_SUCCESS"]
        return 0
    
    @checkPlayerexist
    def server_logout(self,*args):
        msg = args[0]
        id = msg[1]
        addr = self.idtoinfo[id][0]
        self.delplayer(id)
        print 'logout',id
        self.send(self.errormsg["LOGOUT_SUCCESS"],addr)
        return 0
    
    @checkPlayerexist
    def server_list(self,*args):
        msg = args[0]
        addr = msg[-1]
        plist = []
        for key in self.idtoinfo:
            item = self.idtoinfo[key][1:]
            item.append(key)
            item.pop(1)
            plist.append(item)
            #plist.pop(1)
        plist_json = json.dumps(plist)
        self.send("JSON|"+plist_json+"|!",self.addr_change(addr))  
        print 'list'
        return 0
    
    @checkPlayerexist    
    def server_games(self,*args):
        msg = args[0]
        addr = msg[-1]
        plist = []
        #emptygame["name",[id1,id2],[color1,color2],[retry1,retry2],roundnow,[the list of operation]]
        for game in self.gameinfo:
            info = []
            info.append(game[0])
            info.append(game[1].getinfo())
            plist.append(info)
        plist_json = json.dumps(plist)
        self.send("JSON|"+plist_json+"|!",self.addr_change(addr))  
        print 'games'
        return 0
        
    @checkPlayerexist
    def server_join(self,*args):
        #print 'join'
        msg = args[0]
        id = msg[1]
        addr = self.idtoinfo[id][0]
        roomname = msg[2]
        #if self.gameexist(roomname) == -1:
        roomnum = self.gameexist(roomname)
        if roomnum == -1:
            self.send("MSG|No such Room"+roomname+"|!",addr)
        else:
            if self.gameinfo[roomnum][1].join(id,self.idtoinfo[id]):
                self.send("JOIN|"+roomname+"|!",addr)
            else:
                self.send("MSG|Join Failed|!",addr)
        return 0
    
    @checkPlayerexist
    def server_leave(self,*args):
        msg = args[0]
        id = msg[1]
        addr = self.idtoinfo[id][0]
        roomname = msg[2]
        roomnum = self.gameexist(roomname)
        if roomnum == -1:
            self.send("MSG|No such Room"+roomname+"|!",addr)
        else:
            if self.gameinfo[roomnum][1].exit(id,self.idtoinfo[id]):
                self.send("LEAVE|"+roomname+"|!",addr)
            else:
                self.send("MSG|LEAVE Failed|!",addr)
        return 0
    
    def server_msg(self,*args):
        msg = args[0]
        content = msg[1]
        sid = msg[2]
        saddr = self.idtoinfo[sid][0]
        #content = "From player"+str(sid)+":"+content
        dids = msg[3]
        if dids == "-1":
            for id in self.id:
                addr = self.idtoinfo[id][0]
                self.send("MSG|"+content+"|"+str(sid)+"|!",addr)
            return 
        
        dids = msg[3].split(",")
        for did in dids:
            if did not in self.idtoinfo:
                self.send("MSG|"+str(did)+" not online|!", saddr)
                continue
            daddr = self.idtoinfo[did][0]
            if str(daddr) == "-1":
                print content
            self.send("MSG|"+content+"|"+str(sid)+"|!",daddr)
        return 0
    
    #ret = local_cmd[command](sendingqueue,listenqueue,playerlist,gameinfo,ADDR_LISTEN,ADDR_SENDING,ROOM_NUM,n)
    def resetall(self,*args):
        #UNFINISHED
        for id in self.id:
            addr = self.idtoinfo[id][0]
            self.kickplayer([0,id],0)
        self.playerlist=[]
        self.idtoinfo = {}
        self.gameinfo = []
        self.id = []
    
    def kickplayer(self,*args):
        msg = args[0]
        playerid = str(msg[1])
        if playerid not in self.idtoinfo:
            print 'Not Exist ',playerid
            return 0
        else:
            self.send(self.errormsg["KICKED_OUT"],self.idtoinfo[playerid][0])
            self.delplayer(playerid)
            print 'Kicked Out',playerid
            return 0
    
    def showgame(self,*args):
        command = args[0]
        name = command[1]
        index = self.gameexist(name)
        self.gameinfo[index][1].show()
        
    def closegame(self,*args):
        command = args[0]
        try:
            name = command[1]
        except IndexError:
            print "Invalid Operation"
            return 0
        index = self.gameexist(name)
        if index == -1:
            print 'Close Failed'
        else:
            for id in self.gameinfo[index][1].getserverplayer():
                if id == -1:
                    continue
                addr = self.idtoinfo[id][0]
                self.send(self.errormsg["KICKED_OUT"],addr)
                self.delplayer(id)
            closed = self.gameinfo.pop(index)
            print "Close Success"
            
    def opengame(self,*args):
        command = args[0]
        try:
            name = command[1]
        except IndexError:
            print "Invalid Operation"
            return 0
        if self.gameexist(name)>=0:
            print 'Open Failed'
        else:
            newgame = ServerGame()
            self.gameinfo.append([name,newgame])
            print 'Open Success'
        return 0
    
    def stop_server(self,*args):
        print 'stopping Server'
        #print self.sendingqueue
        #self.send("@", self.ADDR_L)
        #print 'sending.done'
        return '@'
    
    def show_n(self,*args):
        print self.n
        return 0
    
    def test(self,*args):
        #self.playerlist.append(1000)
        print self.gameinfo,self.playerlist,self.idtoinfo,self.id
        return 0
    
    
    def disconnect(self,*args):
        print "Here"
        print args
        msg = args[0]
        playeraddr = (msg[1],int(msg[2]))
        playerid = None
        for player in self.idtoinfo:
            if playeraddr in self.idtoinfo[player]:
                playerid = player
                break
        if playerid not in self.idtoinfo:
            print 'Not Exist ',playerid
            return 0
        else:
            self.send(self.errormsg["KICKED_OUT"],self.idtoinfo[playerid][0])
            self.delplayer(playerid)
            print 'Kicked Out',playerid
            return 0
    #INTERNAL FUNC
    def checkallconnection(self):
        #for id in self.idtoinfo:
        #    addr = idtoinfo()
        pass
    
    def delplayer(self,id):
        for room in self.gameinfo:
            detail = room[1]
            if id in room[1].getserverplayer():
                room[1].exit(id,self.idtoinfo[id])
                
        del self.idtoinfo[id]
        self.id.pop(self.id.index(id))
        return 0
    
    def getid(self):
        #here to change the max player
        for i in range(200):
            if str(i) in self.id:
                continue
            else:
                return str(i)
        return -1  
    
    def send(self,str,addr):
        msg = (str,addr)
        #print "Sending:",msg
        self.sendingqueue.put(msg)
    
    def playerexist(self,addr):
        for key in self.idtoinfo:
            if addr in self.idtoinfo[key]:
                return key
        return -1
    
    def addr_change(self,addr):
        addr = list(addr)
        addr[1] -= 1
        return tuple(addr)
    
    def gameexist(self,name):
        if self.ROOM_NUM <= len(self.gameinfo):
            return self.ROOM_NUM + 1
        n = 0
        for game in self.gameinfo:
            if game[0] == name:
                return n
            else:
                n += 1
        return -1