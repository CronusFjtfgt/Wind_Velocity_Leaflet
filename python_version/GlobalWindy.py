# -*- coding: UTF-8 -*-

import json
import sys
import numpy as np

from Windy import *

class GlobalWindy:
    '多风层数据类'

    POINT_NUMBER = 5 #每层分支个数
    MIN_ZONE = 15 #终点区域半径degree
    LAND_ZONE = 3 #近地点起飞范围半径
    MAX_DEEP = 15 #最大递归层数
    MAX_BRANCH = 2 #最多完成路线
    data_path = '../JSON/'
    data_date = '2019061200'
    data_type = [
        '10mab',
        '80mab',
        '100mab',
        '975mb',
        '950mb',
        '925mb',
        '900mb',
        '850mb',
        '800mb',
        '750mb',
        '700mb',
        '650mb',
        '600mb',
        '550mb',
        '500mb',
        '450mb',
        '400mb',
        '350mb',
        '300mb',
        '250mb',
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
    Japan_Korea = [41.66, 126.61, 20.45, 142.65]

    def __init__(self):
        sys.setrecursionlimit(3925)
        for i in range(len(self.data_type)):
            type = self.data_type[i]
            self.DATA[type] = self.data_path + self.data_date + '/' + type + '.json'
            with open(self.DATA[type], 'r') as d:
                data = json.load(d)
                self.WINDY[type] = Windy(data, type)
                self.WINDY[type].clearPartWind(self.Japan_Korea)
                print 'Load:',type
        # ============================= main ==============================
        result, list = self.search_close_area_loop(self.start,self.destiny,'250mb')
        self.rebuild(result, list)
        # ============================= debug =============================
        # print self.WINDY['300mb'].evolvePath(29.9155561812, 142.024638958, self.destiny[0], self.destiny[1])
        # print self.WINDY['300mb'].evolvePath(44.42036278591202, 242.78044887399594, self.destiny[0], self.destiny[1])

    def __getPath(self):
        distance = self.WINDY['250mb'].distance(self.start[0], self.start[1], self.destiny[0], self.destiny[1])
        self.search_close_area([], self.start, self.destiny, '250mb', distance, self.POINT_NUMBER)
        for path in self.AREA_PATH:
            end = path['path'].pop()
            self.MAX_BRANCH = 0
            self.search_land(path['path'], end, self.destiny, end[3], path['distance'])
        self.LAND_PATH.sort(key= lambda i: i['distance'])
        if(self.LAND_PATH):
            for i in range(4):
                print self.LAND_PATH[i],','
        else:
            print 'search false!'

    def switchLayer(self, layerType, probDown = 0.6, probUp = 0.4):
        layer_numb = self.data_type.index(layerType)
        if(layer_numb == 0):
            nextLayer = layer_numb + 1
        elif(layer_numb == len(self.data_type) - 1):
            nextLayer = layer_numb - 1
        else:
            # nextLayer = layer_numb + 1
            nextLayer = layer_numb + np.random.choice([-1,1],None,False,[probDown,probUp])
        # print layerType,'switch to',self.data_type[nextLayer]
        return self.data_type[nextLayer]

    def search_close_area(self, path, start, destiny, type, distance, pointNumber, deep = 0, branches = 0):
        Windy = self.WINDY[type]
        Path = Windy.evolvePath(start[0], start[1], destiny[0], destiny[1])
        closePoint = Path['closePoint']
        if(
                closePoint == []
                or closePoint[3] >= distance
                or deep == self.MAX_DEEP
                or branches == self.MAX_BRANCH
        ):
            print distance,type
            return
        elif(closePoint[3] < self.MIN_ZONE):
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
            # Zone = Windy.selectInZone(Path['path'], closePoint, pointNumber)
            Zone = Windy.selectInPath(Path['path'], pointNumber)
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

    def search_land(self, path, start, destiny, type, distance, pointNumber = 2, deep = 0, branches = 0):
        if(
                type == self.data_type[0]
                # or branches == self.MAX_BRANCH
        ):
            if(distance <= self.LAND_ZONE):
                print 'One Landing Path'
                self.LAND_PATH.append({
                    'path': path,
                    'distance': distance,
                })
                return
            else:
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

    def search_path(self, start, destiny, type, distance, pointNumber, deep = 0, branches = 0):
        Windy = self.WINDY[type]
        Path = Windy.evolvePath(start[0], start[1], destiny[0], destiny[1])
        closePoint = Path['closePoint']
        if(
                closePoint == []
                or closePoint[3] == distance
                or deep == self.MAX_DEEP
                or branches == self.MAX_BRANCH
        ):
            print 'END'
            return {
                'path': [['NULL']],
                'distance': float('inf')
            }
        elif(closePoint[3] < self.MIN_ZONE):
            print 'One Path Complete'
            branches += 1
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
                        pointNumber, deep + 1, branches
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

    def search_close_area_loop(self, start, destiny, type, pointNumber = 5):
        print 'PATH:',destiny,'(',type,') to',start
        Close = []
        end, deep = 0, 0
        point = [49,4,2,2,2,2,2,2,2,2,2,2,2,2]
        dis = self.WINDY[type].distance(start[0], start[1], destiny[0], destiny[1])
        Open = [
            {
                'pre': 'END',
                'node': [start, dis, type],
                'next': type
            }
        ]
        for node in Open:
            Type = node['next']
            Windy = self.WINDY[Type]
            Path = Windy.evolvePath(node['node'][0][0], node['node'][0][1], destiny[0], destiny[1])
            closePoint = Path['closePoint']
            position = Open.index(node)
            if(
                len(Open) >= 21000
                or len(Close) >= self.MAX_BRANCH
                or closePoint == []
            ):
                if(position == end):
                    end = len(Open) - 1
                    deep += 1
                    print 'SEARCHING... ...',Type
                continue
            elif(
                closePoint[3] <= self.MIN_ZONE
            ):
                Close.append(node)
                print node,closePoint
            else:
                Zone = Windy.selectInPath(Path['path'], point[deep])
                Selected = Zone['Selected']
                Cursor = Zone['Cursor']
                Selected.append(closePoint[0 : 2])
                Cursor.append(closePoint[2])
                length = len(Cursor)
                for i in range(length):
                    nextLayer = self.switchLayer(Type, 0.9, 0.1)
                    Open.append(
                        {
                            'pre': position,
                            'node': [
                                Selected[i][0 : 2], Cursor[i],
                                Windy.distance(Selected[i][0], Selected[i][1], destiny[0], destiny[1]),
                                Type
                            ],
                            'next': nextLayer
                        }
                    )
                    if(position == end and i == length - 1):
                        end = len(Open) - 1
                        deep += 1
                        print 'SEARCHING... ...',Type
        Result = Open[:]
        Result.sort(key= lambda i: i['node'][2])
        return Result, Open, Close
        # for i in range(200):
        #     print result[i]

    def rebuild(self, result, list, branches = 5):
        path = []
        for node in result[ : branches]:
            while(node['pre'] != 'END'):
                n = node['node']
                Type = n[3]
                pre = node['pre']
                clip = n[1]
                Path = self.WINDY[Type].evolvePath(n[0][0], n[0][1])[ : clip]
                path += Path
                node = list[pre]
            print path


