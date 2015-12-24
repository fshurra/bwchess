import wx
import threading
import sys,os
from copy import deepcopy
from time import sleep
from bwgame import BWGame
from clientclass import ClientGame
#from curses.ascii import DC1

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
        style =  wx.TE_MULTILINE | wx.TE_RICH #| wx.TE_READONLY
        wx.TextCtrl.__init__(self, parent = parent, id= id, value = value, pos=pos, size=size, style=style, validator=wx.DefaultValidator, name=name)
        self.setStyle(background,wordcolour)
        self.old_stdout=sys.stdout
        self.old_stderr=sys.stderr
        sys.stdout = self
        sys.stderr = self

    def write(self,output):
        output=output.replace('\n','\r\n')
        self.AppendText(output)
        
    def setStyle(self,background = "black", wordcolour = "yellow"):
        self.SetBackgroundColour(background)
        self.SetDefaultStyle(style = wx.TextAttr(wordcolour,background))
        
    def back_to_console(self):
        sys.stdout=self.old_stdout
        sys.stderr=self.old_stderr



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
        dc = wx.ClientDC(self)
        self.draw(dc,data)
    def OnPaint(self,evt):
        dc = wx.BufferedPaintDC(self)
        self.draw(dc,self.gameinfo)
        
class MainFrame(wx.Frame):
    def __init__(self,parent,id,title,style = wx.DEFAULT_FRAME_STYLE, size = (600,450),pos = (100,100),queue = [],game = None):
        wx.Frame.__init__(self,parent = parent,id = id,title = title,style= style,size = size, pos = pos)
        panel = wx.Panel(self,-1)
        self.commandqueue = queue
        self.game = game
        self.board = Board(panel,-1,size = (275,274),pos = (0,0),gameinfo = self.game.getgame(),frame = self)
        self.bu_click = wx.Button(panel,-1,"Test",size = (100,30),pos = (350,370))
        self.shower = new_std(parent = panel,size = (325,274),pos = (275,0))
        self.inputer = new_input(parent = panel,id = -1,value = '',size = (480,20),pos = (100,280))
        self.text1 = wx.StaticText(panel,-1,"Command:",size = (65,20),pos = (20,280))
        self.color = 1
        
        self.myturn = None
        self.clock = wx.Timer(self)
        self.Bind(wx.EVT_BUTTON,self.OnClick_bu_click,self.bu_click)
        self.Bind(wx.EVT_TEXT_ENTER,self.OnEnterText,self.inputer)
        self.Bind(wx.EVT_TIMER,self.OnTimer,self.clock)
        self.clock.Start(100)
    
    def OnEnterText(self,evt):
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
        
    def OnClick_bu_click(self,evt):
        #self.refreshinfo()
        pass
        #self.board.PaintNow(self.game.getgame())
        
    def put(self,x,y):
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