# List have 3 lists MSGDATA PLAYERLIST GAMEINFO SENDQUEUE
# The MSGDATA is like [COMMAND[,detail...],IDENTITY,remote_addr]
import json
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
                           "MSG" : self.server_msg
                           }
        #HERE ARE THE LOCALCMDS
        self.local_cmd = {
                           "stop" : self.stop_server,
                           "show" : self.show_n,
                           "test" : self.test,
                           "opengame" : self.opengame,
                           "closegame" : self.closegame,
                           "reset-all" : self.resetall,
                           'kick' : self.kickplayer
                          }
        self.errormsg = {
                         "PLAYER_FULL": "MSG|The Server is Full|!",
                         "KICKED_OUT": "KO|You have been kicked out|!",
                         "LOGIN_SUCCESS": "MSG|Login Success|!",
                         "LOGOUT_SUCCESS": "MSG|Logged Out|!",
                         "LOGINED" : 'MSG|You Have Already Login!|!'
                         }
    #check all games every time
    def everygame(self):
        pass
    
    #NETWORK FUNC
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
    
    def server_logout(self,*args):
        msg = args[0]
        id = msg[1]
        addr = self.idtoinfo[id][0]
        self.delplayer(id)
        print 'logout',id
        self.send(self.errormsg["LOGOUT_SUCCESS"],addr)
        return 0
    
    def server_list(self,*args):
        msg = args[0]
        addr = msg[-1]
        plist = []
        for key in self.idtoinfo:
            item = self.idtoinfo[key][1:]
            item.append(key)
            plist.append(item)
        plist_json = json.dumps(plist)
        self.send("JSON|"+plist_json+"|!",self.addr_change(addr))  
        print 'list'
        return 0
        
    def server_games(self,*args):
        msg = args[0]
        addr = msg[-1]
        plist = []
        #emptygame["name",[id1,id2],[color1,color2],[retry1,retry2],roundnow,[the list of operation]]
        for game in self.gameinfo:
            info = []
            info.append(game[0])
            info.append(game[1])
            plist.append(info)
        plist_json = json.dumps(plist)
        self.send("JSON|"+plist_json+"|!",self.addr_change(addr))  
        print 'games'
        return 0
        
    def server_join(self,*args):
        print 'join'
        return 0
    
    def server_msg(self,*args):
        return 0
    
    #ret = local_cmd[command](sendingqueue,listenqueue,playerlist,gameinfo,ADDR_LISTEN,ADDR_SENDING,ROOM_NUM,n)
    def resetall(self,*args):
        #UNFINISHED
        self.playerlist=[]
        self.idtoinfo = {}
        self.gameinfo = []
        self.id = []
    
    def kickplayer(self,*args):
        msg = args[0]
        playerid = str(args[1])
        if playerid not in self.idtoinfo:
            print 'Not Exist ',playerid
            return 0
        else:
            self.send(self.errormsg["KICKED_OUT"],self.idtoinfo[playerid][0])
            self.delplayer(playerid)
            print 'Kicked Out',playerid
            return 0
        
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
            for id in self.gameinfo[index][1]:
                if id == -1:
                    continue
                addr = self.idtoinfo[id][0]
                self.send(self.errormsg["KICKED_OUT"],addr)
            self.gameinfo.pop(index)
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
            self.gameinfo.append([name,[-1,-1],[8,8],[0,0],0,[]])
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

    #INTERNAL FUNC
    
    def delplayer(self,id):
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