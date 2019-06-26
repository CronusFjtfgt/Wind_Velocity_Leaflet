import Server
import Main

if(__name__ == '__main__'):
    Server.new_service()
    while(True):
        Server.recieveSignal()