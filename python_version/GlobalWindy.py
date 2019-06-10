# -*- coding: UTF-8 -*-

import json
import sys
import numpy as np

from Windy import *

class GlobalWindy:
    '多风层数据类'

    POINT_NUMBER = 4 #每层分支个数
    NEAR_ZONE = 15 #终点区域半径degree
    MAX_DEEP = 20 #最大递归层
    MAX_BRANCH = 2 #最大完成路线
    branches = 0 #初始完成路线
    data_path = '../JSON/'
    data_type = [
        '10m',
        '100m',
        '50mb',
        '100mb',
        '200mb',
        '250mb'
    ]
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
    AREA_PATH = []
    LAND_PATH = []
    SORT_PATH = []
    # start = [-10, 109]
    # destiny = [31, 258]
    destiny = [31.8, 103.8]
    start = [37.72, 261.9]

    def __init__(self):
        sys.setrecursionlimit(3925)
        for i in range(len(self.data_name)):
            type = self.data_type[i]
            self.DATA[type] = self.data_path + self.data_name[i]
            with open(self.DATA[type], 'r') as d:
                data = json.load(d)
                self.WINDY[type] = Windy(data, type)
                print 'Load:',type
        # ============================= main =============================
        distance = self.WINDY['250mb'].distance(self.start[0], self.start[1], self.destiny[0], self.destiny[1])
        self.search_close_area([], self.start, self.destiny, '250mb', distance, self.POINT_NUMBER)
        for path in self.AREA_PATH:
            end = path['path'].pop()
            self.MAX_BRANCH = 0
            self.search_land([], end, self.destiny, end[3], path['distance'])
        # print sorted(self.LAND_PATH, key= lambda i: i['distance'])
        for p in self.LAND_PATH:
            print p,','
        # ============================= debug =============================
        # print self.WINDY['100mb'].evolvePath(self.start[0], self.start[1], self.destiny[0], self.destiny[1])
        # print self.WINDY['100m'].evolvePath(37.84832850292116, 118.80936439002505)

    def switchLayer(self, layerType, probDown = 0.6, probUp = 0.4):
        layer_numb = self.data_type.index(layerType)
        if(layer_numb == 0):
            nextLayer = layer_numb + 1
        elif(layer_numb == len(self.data_type) - 1):
            nextLayer = layer_numb - 1
        else:
            # nextLayer = layer_numb + 1
            nextLayer = layer_numb + np.random.choice([-1,1],None,False,[probDown,probUp])
        print layerType,'switch to',self.data_type[nextLayer]
        return self.data_type[nextLayer]

    def search_close_area(self, path, start, destiny, type, distance, pointNumber, deep = 0, branches = 0):
        Windy = self.WINDY[type]
        Path = Windy.evolvePath(start[0], start[1], destiny[0], destiny[1])
        closePoint = Path['closePoint']
        if(
                closePoint == []
                or closePoint[3] == distance
                or deep == self.MAX_DEEP
                or branches == self.MAX_BRANCH
        ):
            return
        elif(closePoint[3] < self.NEAR_ZONE):
            print 'One Path Complete'
            branches += 1
            cur_p = Path['path'][: closePoint[2] + 1]
            p = path + cur_p
            self.AREA_PATH.append({
                'path': p,
                'distance': closePoint[3],
            })
            return
        else:
            Zone = Windy.selectInZone(Path['path'], closePoint, pointNumber)
            Selected = Zone['Selected']
            Cursor = Zone['Cursor']
            for i in range(pointNumber):
                # print 'cursor,point:',Cursor[i],Selected[i]
                tp = path + Path['path'][: Cursor[i] + 1]
                self.search_close_area(
                    tp, Selected[i], destiny, self.switchLayer(type),
                    Windy.distance(Selected[i][0], Selected[i][1], destiny[0], destiny[1]),
                    pointNumber, deep + 1, branches + 1
                )

    def search_path(self, start, destiny, type, distance, pointNumber, deep = 0):
        Windy = self.WINDY[type]
        Path = Windy.evolvePath(start[0], start[1], destiny[0], destiny[1])
        closePoint = Path['closePoint']
        if(
                closePoint == []
                or closePoint[3] == distance
                or deep == self.MAX_DEEP
                or self.branches == self.MAX_BRANCH
        ):
            print 'END'
            return {
                'path': [['NULL']],
                'distance': float('inf')
            }
        elif(closePoint[3] < self.NEAR_ZONE):
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
            Zone = Windy.selectInZone(Path['path'], closePoint, pointNumber)
            Selected = Zone['Selected']
            Cursor = Zone['Cursor']
            for i in range(len(Selected)):
                # print 'cursor,point:',Cursor[i],Selected[i]
                sPath.insert(
                    i,
                    self.search_path(
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
            else:
                mainPath = [['NULL']]
            return {
                'path': mainPath,
                'distance': min(dis)
            }

    def search_land(self, path, start, destiny, type, distance, pointNumber = 2, deep = 0, branches = 0):
        if(
                type == self.data_type[0]
                # or branches == self.MAX_BRANCH
        ):
            print 'One Landing Path'
            self.LAND_PATH.append({
                'path': path,
                'distance': distance,
            })
            return
        else:
            downLayer = self.switchLayer(type, 1, 0)
            Windy_down = self.WINDY[downLayer]
            Path_down = Windy_down.evolvePath(start[0], start[1], destiny[0], destiny[1])
            closePoint = Path_down['closePoint']
            Zone = Windy_down.selectInPath(Path_down['path'], pointNumber)
            if(Zone):
                Selected = Zone['Selected']
                Cursor = Zone['Cursor']
                for i in range(len(Cursor)):
                    tp = path + Path_down['path'][: Cursor[i] + 1]
                    self.search_land(
                        tp, Selected[i], destiny, downLayer,
                        Windy_down.distance(Selected[i][0], Selected[i][1], destiny[0], destiny[1]),
                        pointNumber, deep + 1, branches + 1
                    )
            else:
                self.search_land(
                        path, path[-1], destiny, downLayer,distance,
                        pointNumber, deep + 1, branches + 1
                    )

