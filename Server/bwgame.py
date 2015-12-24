# this is the bwchess game it self
#the game is a 8x8 one
import copy


    


class BWGame:
    # in the game the -1 empty 0 white 1 black
    # the vars here
    # game maybe can change to np.array later
    # prevgame
    # count   actual it is the round of this play
    # hist
    # player
    '''
    game()         #The chess play
    put(row,column,color)
    checkposition(row,column,color)
    show()
    '''
    def __init__(self):
        self.game = [];
        for i in range(8):
            line = []
            for j in range(8):
                line.append(-1)
            self.game.append(line)
        
        self.count = 0
        self.player = [['',1],['',0]]
        #need to add the chosing b/w here
        self.game[3][3] = 1
        self.game[4][4] = 1
        self.game[3][4] = 0
        self.game[4][3] = 0
        self.prevgame = copy.deepcopy(self.game)
        self.hist = []
    
    
    def setplayer(self,playername,color):
        if int(color) == 1:
            self.player[0][1] = playername
        elif int(color) == 0:
            self.player[1][1] = playername
        else:
            print "error happened"
        return 
              
    def put(self,x,y,color):
        # x, y in the range of the game yard and the player is 0 or 1
        # if illegal to put return 2
        # if it is using the #pass the x and y should be -1,-1
        self.prevgame = copy.deepcopy(self.game)
        if x == -1:
            #PASS
            print "PASS"
            self.count+=1
            count = self.count
            self.hist.append([count,x,y,color,"PASS"])
            return 0;
        
        if self.checkposition(x, y, color) != -1:
            print "Cannot put there"
            return -1
        # backup the previous
        # get the color of the player who put here
        self.game[x][y] = color
        count = self.count
        self.hist.append([count,x,y,color])
        self.count+=1
        #refresh the game to the after turning
        self.afterput(x,y,color)
        return 1
        
    def unput(self):
        # restore the game into the previous situation
        unputed = self.hist.pop()
        self.game = copy.deepcopy(self.prevgame)
        return unputed
    
    def checkturning(self,x,y,color):
        # returning the turning direction number to put an color in the xy place
        dirs = [[-1,-1],[-1,0],[-1,1],[0,-1],[0,1],[1,-1],[1,0],[1,1]]
        changed = 0 
        #it is still changed direction now
        # using width searching here to judge the afterput situation
        nextdirs = copy.deepcopy(dirs)
        for i in range(1,8):
            prevdirs = nextdirs
            nextdirs = []
            for dir in prevdirs:
                _x = x
                _y = y
                _x += i*dir[0]
                _y += i*dir[1]
                if (_x<0 or _x>7) or (_y<0 or _y>7):
                    continue
                if self.game[_x][_y] == -1:
                    continue
                if self.game[_x][_y] == color:
                    if self.countturning(x,y,_x,_y,color,dir) == 0:
                        continue
                    changed += 1
                    #here is from the turning one ,may have better one to do this
                    continue
                nextdirs.append(dir)
        return changed
    
    def checkposition(self,x,y,color):
        # will return the chess number -1,0,1
        # and sth else to make sure the position is good for putting
        # if good return -1(means empty) 
        # illegal point will return other
        posinf = self.game[x][y]
        turnings = self.checkturning(x, y, color)
        print turnings
        if turnings == 0:
            return 2
        return posinf
    
    def countturning(self,x,y,_x,_y,color,dir):
        x0 = x
        y0 = y
        turncount = 0
        while(True):
            x0 += dir[0]
            y0 += dir[1]
            if x0 == _x and y0 == _y:
                break;
            turncount += 1
            #self.game[x0][y0] = color
        return turncount
    
    def turnbetween(self,x,y,_x,_y,color,dir):    
        x0 = x
        y0 = y
        while(True):
            x0 += dir[0]
            y0 += dir[1]
            if x0 == _x and y0 == _y:
                break;
            self.game[x0][y0] = color
        return 1
    
    def afterput(self,x,y,color):
        # to check the game situation and do the turning 
        dirs = [[-1,-1],[-1,0],[-1,1],[0,-1],[0,1],[1,-1],[1,0],[1,1]]
        changed = 0 #it is still changed direction now
        # using width searching here to judge the afterput situation
        nextdirs = copy.deepcopy(dirs)
        for i in range(1,8):
            prevdirs = nextdirs
            nextdirs = []
            for dir in prevdirs:
                _x = x
                _y = y
                _x += i*dir[0]
                _y += i*dir[1]
                if (_x<0 or _x>7) or (_y<0 or _y>7):
                    #position out delet the direction
                    #dirs.remove(dir)
                    continue
                if self.game[_x][_y] == -1:
                    #dirs.remove(dir)
                    continue
                if self.game[_x][_y] == color:
                    #get a same then turning and end this dir
                    changed+=1
                    self.turnbetween(x,y,_x,_y,color,dir)
                    #dirs.remove(dir)
                    continue
                nextdirs.append(dir)
        return changed
        
    def getgame(self):
        #returning the game matrix
        return self.game
    
    def show(self):
        #for debugging usage
        showing = copy.deepcopy(self.game)
        for line in showing:
            print line
        for i in range(len(showing)):
            for j in range(len(showing[i])):
                if showing[i][j] == -1:
                    showing[i][j] = 8
        for line in showing:
            print line

            
            
if __name__ =="__main__":
    b = BWGame("p1","p2")
    b.show()
    b.put(0,0,1)
    b.show()
    b.put(0,1,0)
    b.show()
    b.put(0,2,1)
    b.show()
    b.put(3,2,0)
    b.show()
    b.put(2,2,0)
    print b.count