# List have 3 lists MSGDATA PLAYERLIST GAMEINFO SENDQUEUE
# The MSGDATA is like [COMMAND[,detail...],IDENTITY,remote_addr]

def server_login(*list):
    print 'login'

def server_logout(*list):
    print 'logout'

def server_list(*list):
    print 'list'
    
def server_games(*list):
    print 'games'
    
def server_join(*list):
    print 'join'
    


server_cmd = {
              "LOGIN" : server_login,
              "LOGOUT" : server_logout,
              "LIST" : server_list,
              "GAMES" : server_games,
              "JOIN" : server_join
              }


