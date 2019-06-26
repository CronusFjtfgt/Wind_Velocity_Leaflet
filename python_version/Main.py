# -*- coding: UTF-8 -*-
import sys
sys.setrecursionlimit(3925)
from GlobalWindy import *
from Server import Server

def str2float(str):
    lat = float(str[0])
    lng = float(str[1])
    return [lat,lng]



if(__name__ == '__main__'):
    # server = Server()
    # server.new_service()
    # server.debug('debug')
    if(len(sys.argv) > 1):
        str_s = sys.argv[1:3]
        str_d = sys.argv[3:]
        start = str2float(str_s)
        destiny = str2float(str_d)
        globalWindy = GlobalWindy(start, destiny)
    else:
        start = [41.244772343082076,105.64453125000001 ]
        destiny = [33.974795334774505, 100.95025301820137]
        globalWindy = GlobalWindy(start, destiny)