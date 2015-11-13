# this is the bwchess game it self
#the game is a 8x8 one


class BWGame:
    # in the game the -1 empty 0 white 1 black
    # the vars here
    # game maybe can change to np.array later
    # prevgame
    # count   acturall it is the round of this play
    # hist
    # player
    def __init__(self,player1,player2):
        self.game = [];
        for i in range(8):
            line = []
            for j in range(8):
                line.append(-1)
            self.game.append(line)
        
        self.count = 1
        self.player = [["player1",1],["player2",0]]
        #need to add the chosing b/w here
        self.game[3][3] = 1
        self.game[4][4] = 1
        self.game[3][4] = 0
        self.game[4][3] = 0
        self.prevgame = self.game
        self.hist = []
              
    def put(self,x,y,color):
        # x, y in the range of the game yard and the player is 0 or 1
        # if illegal to put return 2
        # if it is using the #pass the x and y should be -1,-1
        self.prevgame = self.game
        if x == -1:
            #PASS
            self.count+=1
            count = self.count
            self.hist.append([count,x,y,color,"PASS"])
            return 0;
        
        if self.checkposition(x, y, color) != -1:
            return -1;
        # backup the previous
        # get the color of the player who put here
        self.game[x][y] = color
        self.count+=1
        count = self.count
        self.hist.append([count,x,y,color])
        #refresh the game to the after turning
        self.afterput(x,y,color)
        return 1
        
    def unput(self):
        # restore the game into the previous situation
        unputed = self.hist.pop()
        self.game = self.prevgame
        return unputed
    
    def checkposition(self,x,y,color):
        # will return the chess number -1,0,1
        # and sth else to make sure the position is good for putting
        # if good return -1(means empty) 
        posinf = self.game[x][y]
        return posinf
    
    def turnbetween(self,x,y,_x,_y,color,dir):    
        while(True):
            __x = x + dir[0]
            __y = y + dir[1]
            if __x == _x:
                break;
            self.game[__x][__y] = color
        return 1
    
    def afterput(self,x,y,color):
        # to check the game situation and do the turning
        dirs = [[-1,-1],[-1,0],[-1,1],[0,-1],[0,1],[1,-1],[1,0],[1,1]]
        changed = 0 #it is still changed direction now
        # using width searching here to judge the afterput situation
        for i in range(1,8):
            for dir in dirs:
                _x = x
                _y = y
                _x += dirs[0]*i
                _y += dirs[1]*i
                if (_x<0 or _x>7) or (_y<0 or _y>7):
                    #position out delet the direction
                    dirs.remove(dir)
                if self.game[_x][_y] == -1:
                    dirs.remove(dir)
                if self.game[_x][_y] == color:
                    #get a same then turning and end this dir
                    changed+=1
                    self.turnbetween(x,y,_x,_y,color,dir)
                    dirs.remove(dir)
        return changed
        
    def getgame(self):
        #returning the game matrix
        return self.game