# -*- coding: UTF-8 -*-

import sys
sys.setrecursionlimit(3925)
from Windy import *

class GlobalWindy:
    '多风层数据类'

    POINT_NUMBER = 2 #每层分支个数
    CLOSE_ZONE = 2 #degree
    MAX_DEEP = 10
    MAX_BRANCH = 10
    branches = 0
    data_path = '../JSON/'
    data_type = ['10m', '100m', '50mb', '100mb', '200mb', '250mb']
    data_name = [
        '2019052218_10m.json',
        '2019052218_100m.json',
        '2019052218_50mb.json',
        '2019052218_100mb.json',
        '2019052218_200mb.json',
        '2019052218_250mb.json',
    ]
    DATA = {}
    GRID = {}
    WINDY = {}
    start = [39, 112]
    destiny = [34, 261.39]

    def __init__(self):
        for i in range(len(self.data_name)):
            type = self.data_type[i]
            self.DATA[type] = self.data_path + self.data_name[i]
            with open(self.DATA[type], 'r') as d:
                data = json.load(d)
                self.WINDY[type] = Windy(data, type)
                print 'Load:',type
        distance = self.WINDY['10m'].distance(self.start[0], self.start[1], self.destiny[0], self.destiny[1])
        dis = self.searchPath(self.start, self.destiny, '10m', distance, self.POINT_NUMBER)
        print dis
        # wind = self.WINDY['10m']
        # Path = wind.evolvePath(self.start[0], self.start[1], self.destiny[0], self.destiny[1])
        # selected =  wind.searchZone(Path['path'], Path['closePoint'], 2)
        # print selected

    def switchLayer(self, layerType):
        layer_numb = self.data_type.index(layerType)
        if(layer_numb == 0):
            nextLayer = layer_numb + 1
        elif(layer_numb == len(self.data_type) - 1):
            nextLayer = layer_numb - 1
        else:
            # nextLayer = layer_numb + 1
            nextLayer = layer_numb + random.choice([-1, 1])
        return self.data_type[nextLayer]

    def searchPath(self, start, destiny, type, distance, pointNumber, deep = 0):
        Windy = self.WINDY[type]
        Path = Windy.evolvePath(start[0], start[1], destiny[0], destiny[1])
        closePoint = Path['closePoint']
        if(
                closePoint == []
                or closePoint[3] == distance
                or deep > self.MAX_DEEP
                or self.branches == self.MAX_BRANCH
        ):
            return {
                'path': [['NULL']],
                'distance': float('inf')
            }
        elif(closePoint[3] < self.CLOSE_ZONE):
            print 'One Path Complete'
            self.branches += 1
            return {
                'path': Path['path'][: closePoint[2] + 1],
                'distance': closePoint[3]
            }
        else:
            sPath = []
            # tp = []
            path = []
            dis = []
            Zone = Windy.searchZone(Path['path'], closePoint, pointNumber)
            Selected = Zone['Selected']
            Cursor = Zone['Cursor']
            for i in range(len(Selected)):
                # print type,' point:',Selected[i]
                sPath.insert(
                    i,
                    self.searchPath(
                        Selected[i], destiny, self.switchLayer(type),
                        Windy.distance(Selected[i][0], Selected[i][1], destiny[0], destiny[1]),
                        pointNumber, deep + 1
                    )
                )
                # tp.insert(i, sPath[i]['type'])
                dis.insert(i, sPath[i]['distance'])
                path.insert(i, sPath[i]['path'])

            minPoint = dis.index((min(dis)))
            # short_type = tp[minPoint]
            short_path = path[minPoint]
            if('NULL' not in short_path[0]):
                mainPath = Path['path'][: Cursor[minPoint] + 1]
                mainPath.extend(short_path)
                print 'mainpath: ',mainPath
            else:
                mainPath = [['NULL']]
            return {
                'path': mainPath,
                'distance': min(dis)
            }

