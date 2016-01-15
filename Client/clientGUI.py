import wx
import threading
import sys,os
from copy import deepcopy
from time import sleep
from bwgame import BWGame
from clientclass import ClientGame
import ConfigParser
#from curses.ascii import DC1

#def writeBlankcfg():

class WXThread(threading.Thread):
    def __init__(self,threadnum,func,*funcargs):
        threading.Thread.__init__(self)
        self.threadNum = threadnum
        self.func = func
        self.funcargs = funcargs
        self.stopflag = threading.Event()
        
    def run(self):
        self.func(self.funcargs)
     
class new_input(wx.TextCtrl):
    def __init__(self,parent, id, value,pos, size,background = "black", wordcolour = "yellow"):
        style = wx.TE_RICH2 | wx.TE_PROCESS_ENTER
        wx.TextCtrl.__init__(self, parent = parent, id= id, value = value, pos=pos,style = style, size=size, validator=wx.DefaultValidator)
        self.setStyle(background,wordcolour)
    def setStyle(self,background = "black", wordcolour = "yellow"):
        #print 'setStyle of input'
        self.SetBackgroundColour(background)
        self.SetDefaultStyle(style = wx.TextAttr(wordcolour,background))
        
class new_std(wx.TextCtrl):
    def __init__(self,parent, id=-1, value='', pos=wx.DefaultPosition, size=wx.DefaultSize, name=wx.TextCtrlNameStr,background = "black", wordcolour = "yellow"):
        style =  wx.TE_MULTILINE | wx.TE_RICH | wx.TE_READONLY
        wx.TextCtrl.__init__(self, parent = parent, id= id, value = value, pos=pos, size=size, style=style, validator=wx.DefaultValidator, name=name)
        self.setStyle(background,wordcolour)
        self.old_stdout=sys.stdout
        self.old_stderr=sys.stderr
        sys.stdout = self
        sys.stderr = self

    def write(self,output):
        try:
            output=output.replace('\n','\r\n')
            self.AppendText(output)
        except Exception as e:
            #print e
            #print "err"
            a = 1
        return 
        
    def setStyle(self,background = "black", wordcolour = "yellow"):
        self.SetBackgroundColour(background)
        self.SetDefaultStyle(style = wx.TextAttr(wordcolour,background))
        
    def back_to_console(self):
        sys.stdout=self.old_stdout
        sys.stderr=self.old_stderr

class info_display(wx.TextCtrl):
    def __init__(self,parent, id=-1, value='', pos=wx.DefaultPosition, size=wx.DefaultSize, name=wx.TextCtrlNameStr,background = "black", wordcolour = "yellow"):
        style =  wx.TE_MULTILINE | wx.TE_READONLY
        wx.TextCtrl.__init__(self, parent = parent, id= id, value = value, pos=pos, size=size, style=style, validator=wx.DefaultValidator, name=name)
        #self.setStyle(background,wordcolour)
    
    def refresh(self,info):
        info = list(info)
        #info = info.sort(key=lambda x: x[0])
        str = ""
        for line in info:
            line = '\t'.join(line)
            str += line+"\n"
        self.Clear()
        self.AppendText(str) 
            

class Board(wx.Window):
    def __init__(self,parent,id,size = (300,300),pos = (0,0),gameinfo = [],frame = None):
        wx.Window.__init__(self,parent = parent, id = id, size = size, pos = pos)
        self.back_bitmap = wx.Bitmap("./pic/panel.png",wx.BITMAP_TYPE_PNG)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.gameinfo = gameinfo
        self.Bind(wx.EVT_LEFT_UP,self.OnLeftUp)
        self.frame = frame
        
    def put(self,pos):
        middle = 31.5
        x = pos[0]
        y = pos[1]
        if x <= 10 or x >= 263:
            return 
        if y <= 10 or y >= 263:
            return
        x = int((pos[0]-10)/middle)
        y = int((pos[1]-10)/middle)
        
        self.frame.put(x,y)
    
    def OnLeftUp(self,evt):
        pos = evt.GetPositionTuple()
        self.put(pos)
        
    def drawPoint(self,dc,x,y,info):
        base = (10,10)
        end = (263,263)
        radix = 14
        # 0 white 1 black
        if int(info) == 1:
            dc.SetPen(wx.Pen('black'))
            dc.SetBrush(wx.Brush("black"))
        elif int(info) == 0:
            dc.SetPen(wx.Pen('white'))
            dc.SetBrush(wx.Brush("white"))
        x_pos = int((end[0]-base[0])*x/8.0 + (end[0]-base[0])/16.0)+10
        y_pos = int((end[0]-base[0])*y/8.0 + (end[0]-base[0])/16.0)+10
        dc.DrawCircle(x_pos,y_pos,radix)
    
    def draw(self,dc,data):
        dc.DrawBitmap(self.back_bitmap,0,0,False)
        for i in range(8):
            for j in range(8):
                if data[i][j] == 1:
                    self.drawPoint(dc,i,j,1)
                if data[i][j] == 0:
                    self.drawPoint(dc,i,j,0)

        
    def PaintNow(self,data):
        #print "print now"
        dc = wx.BufferedDC(wx.ClientDC(self))
        self.draw(dc,data)
        
    def OnPaint(self,evt):
        dc = wx.BufferedPaintDC(self)
        self.draw(dc,self.gameinfo)
        
class MainFrame(wx.Frame):
    def __init__(self,parent,id,title,style = wx.DEFAULT_FRAME_STYLE, size = (600,450),pos = (100,100),queue = [],game = None):
        wx.Frame.__init__(self,parent = parent,id = id,title = title,style= style,size = size, pos = pos)
        panel = wx.Panel(self,-1)
        self.SetIcon(wx.Icon(name='./pic/b.ico', type=wx.BITMAP_TYPE_ICO))
        self.commandqueue = queue
        self.game = game
        self.board = Board(panel,-1,size = (275,274),pos = (0,0),gameinfo = self.game.getgame(),frame = self)
        #self.bu_click = wx.Button(panel,-1,"Test",size = (100,30),pos = (350,370))
        self.shower = new_std(parent = panel,size = (325,274),pos = (275,0))
        self.inputer = new_input(parent = panel,id = -1,value = '',size = (480,20),pos = (100,280))
        self.text1 = wx.StaticText(panel,-1,"Command:",size = (65,20),pos = (20,280))
        self.color = 1
        self.currentinfo = {
                            "Logined" : False,
                            "Roomname" : "",
                            "Playing" : False, 
                            "Id" : -1,
                            "Round" : 0
                        
                            }
        self.myturn = None
        self.clock = wx.Timer(self)
        self.info = wx.StaticText(parent = panel,id = -1,label = "",pos = (0,300),size = (220,100))
        #self.Bind(wx.EVT_BUTTON,self.OnClick_bu_click,self.bu_click)
        self.Bind(wx.EVT_TEXT_ENTER,self.OnEnterText,self.inputer)
        self.Bind(wx.EVT_TIMER,self.OnTimer,self.clock)
        
        
        
        self.bu_login = wx.Button(panel,-1,"Login/out",size = (100,30),pos = (490,300))
        self.bu_games = wx.Button(panel,-1,"Games",size = (100,30),pos = (380,300))
        self.bu_list = wx.Button(panel,-1,"List",size = (100,30),pos = (380,350))
        self.bu_join = wx.Button(panel,-1,"Join/Leave",size = (100,30),pos = (270,350))
        self.bu_setting = wx.Button(panel,-1,"Setting",size = (100,30),pos = (490,350))
        self.bu_msg = wx.Button(panel,-1,"Message",size = (100,30),pos = (270,300))
        self.Bind(wx.EVT_BUTTON,self.OnClick_bu_login,self.bu_login)
        self.Bind(wx.EVT_BUTTON,self.OnClick_bu_games,self.bu_games)
        self.Bind(wx.EVT_BUTTON,self.OnClick_bu_list,self.bu_list)
        self.Bind(wx.EVT_BUTTON,self.OnClick_bu_join,self.bu_join)
        self.Bind(wx.EVT_BUTTON,self.OnClick_bu_setting,self.bu_setting)
        self.Bind(wx.EVT_BUTTON,self.OnClick_bu_msg,self.bu_msg)
        
        self.bu_retry = wx.Button(panel,-1,"Retry",size = (50,30),pos = (220,350))
        self.Bind(wx.EVT_BUTTON,self.OnClick_bu_retry,self.bu_retry)
        
        self.clock.Start(100)
        self.n =0
        #self.ShowCurrentInfo()
        
    def OnClick_bu_login(self,evt):
        if self.currentinfo["Logined"]:
            self.commandqueue.put("logout")
        else:
            conf = ConfigParser.ConfigParser()
            conf.read("client.ini")
            ADDR = conf.get("setting","s_addr")
            LISTEN = conf.get("setting","s_port")
            unameD = wx.TextEntryDialog(self,message = "enter yourname (no space or \"|\" allowed)",caption = u"login", style = wx.OK)
            if unameD.ShowModal() == wx.ID_OK:
                if unameD.GetValue() != "":
                    uname = unameD.GetValue()
                    uname = str(uname)
                else:
                    uname = "None"
            self.commandqueue.put("login "+uname+" "+ADDR+" "+LISTEN)
    def OnClick_bu_games(self,evt):
        self.commandqueue.put("games")
    def OnClick_bu_list(self,evt):
        self.commandqueue.put("list")
    def OnClick_bu_join(self,evt):
        
        if self.currentinfo["Roomname"] != "":
            self.commandqueue.put("leave")
            return 
        unameD = wx.TextEntryDialog(self,message = "enter roomname (no space or \"|\" allowed)",caption = u"join", style = wx.OK)
        if unameD.ShowModal() == wx.ID_OK:
            if unameD.GetValue() != "":
                name = unameD.GetValue()
                name = str(name)
            else:
                name = "None"
        self.commandqueue.put("join "+name)
        return 
    def OnClick_bu_setting(self,evt):
        wx.MessageBox(u"Please close the game and change the client.ini \n This Program is By Feng Suo 13307130084",caption = u"Setting",style = wx.OK)
    def OnClick_bu_msg(self,evt):
        unameD = wx.TextEntryDialog(self,message = "enter messagecontent (no  \"|\" allowed)",caption = u"Message", style = wx.OK)
        if unameD.ShowModal() == wx.ID_OK:
            if unameD.GetValue() != "":
                name = unameD.GetValue()
                name = str(name)
            else:
                name = "None"
        command = "msg "+name+ " "
        unameD = wx.TextEntryDialog(self,message = "enter destination (leave empty to send to all,use \"\,\" in the middle) (no  \"|\" allowed)",caption = u"Message", style = wx.OK)
        if unameD.ShowModal() == wx.ID_OK:
            if unameD.GetValue() != "":
                name = unameD.GetValue()
                name = str(name)
            else:
                name = "-1"
        command = command+name
        self.commandqueue.put(command)
        
        
    def OnClick_bu_retry(self,evt):
        self.ShowCurrentInfo()
        self.commandqueue.put("retry")
         
    def getcurrentinfo(self):
        info = ""
        for key in self.currentinfo:
            if key == "Roomname":
                info += "Room"
            else:
                info += key
            info += "\t\t"+str(self.currentinfo[key])+"\n"
        color = self.game.getmycolor()
        colorinfo = ''
        turninfo = ''
        if color == -1:
            colorinfo = "Color\t\tNone\n"
            info += colorinfo
            return info
        elif color == 1:
            colorinfo = "Color\t\tBlack\n"
        elif color == 0:
            colorinfo = "Color\t\tWhite\n"
        if self.currentinfo["Round"]%2 == color:
            turninfo = "Myturn\n"
        else:
            turninfo = "NotMyturn\n"
        info += colorinfo + turninfo
        type(info)
        return info
    
    def ShowCurrentInfo(self):
        self.currentinfo = self.game.getinfo()
        self.info.SetLabel(self.getcurrentinfo())
    
    def OnEnterText(self,evt):
    
        self.ShowCurrentInfo()
        command = self.inputer.GetValue()
        if command == '':
            return 0
        else:
            self.commandqueue.put(command)
        self.inputer.Clear()
        self.inputer.setStyle()
        print command
        
    def OnTimer(self,evt):
        #pass
        self.board.PaintNow(self.game.getgame())
        if self.n < 6:
            self.n += 1
        else:
            self.n = 0
            self.ShowCurrentInfo()
        #self.ShowCurrentInfo()
        #self.currentinfo = self.game.getinfo()
        
    def OnClick_bu_click(self,evt):
        #self.refreshinfo()
        self.ShowCurrentInfo()
        #self.board.PaintNow(self.game.getgame())
        
    def put(self,x,y):
        self.ShowCurrentInfo()
        color = self.game.getmycolor()
        self.commandqueue.put("put "+str(x)+" "+str(y)+" "+str(color))

        
class BWchessApp(wx.App):
    def __init__(self,commandqueue,game):
        wx.App.__init__(self)
        self.commandqueue = commandqueue
        style = (wx.MINIMIZE_BOX |wx.CLOSE_BOX | wx.CAPTION | wx.SYSTEM_MENU)
        self.frame = MainFrame(parent = None, id = -1, title = u"BWchess", style = style, queue = self.commandqueue,game = game)
        self.frame.Show()
        self.SetTopWindow(self.frame)
        #return True
if __name__ == "__main__":
    game = ClientGame()
    app = BWchessApp([],game)
    #print"Before Main Loop"
    #os.system("echo off")
    app.MainLoop()
    #print"After MainLoop"