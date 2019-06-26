# -*- coding: UTF-8 -*-

import json
import sys
from os import path as pa
import time
import numpy as np

from Windy import *

class GlobalWindy:
    '多风层数据类'
    root = pa.abspath(pa.dirname(__file__)+pa.sep+"..")
    POINT_NUMBER = 5 #每层分支个数
    MIN_ZONE = 5 #终点区域半径degree
    LAND_ZONE = 3 #近地点起飞范围半径
    MAX_DEEP = 15 #最大递归层数
    MAX_BRANCH = 5 #最多完成路线
    POOL_NUMBER = 5 #池化节点数
    data_path = root + '\JSON'
    data_date = '/2019061200'
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
    start = []
    destiny = []
    FINAL_PATH = []

    Japan_Korea = [41.66, 126.61, 30.45, 142.65]

    def __init__(self, start, destiny):
        self.start = start
        self.destiny = destiny
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
        branches = [
            [49,14,14,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2],
            [28,14,9,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2],
            [14,9,9,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2],
            [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2],
            [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2],
            [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2],
            [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2],
        ]

        PATH = self.hierarchical_searche(self.start, self.destiny, branches)
        self.savePath(PATH)
        # ============================= debug =============================
        # print self.WINDY['300mb'].evolvePath(39, 261, 37, 112)
        # print self.WINDY['300mb'].evolvePath(32.403055485197974, 142.22104635893092, -1, -1, False)

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

    def savePath(self, path):
        print '------------------------------ SEARCH END ------------------------------\r\n'
        with open('..\PATH\Record.json', 'w') as f:
            json.dump(path, f)

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

    def search_path_loop(self, start, destiny, type, max_step, branches, pNumb = 5):
        print 'SEARCHING PATH:', start, 'to', destiny, '(',type,')'
        print  '  STR In ',time.asctime(time.localtime(time.time()))
        Close = []
        end, deep = 0, 0
        dis = self.WINDY[type].distance(start[0], start[1], destiny[0], destiny[1])
        Open = [
            {
                'pre': 0,
                'cursor': 0,
                'type': type,
                'node': [destiny, dis],
                'next': type
            }
        ]
        for node in Open:
            Type = node['next']
            Windy = self.WINDY[Type]
            Path = Windy.evolvePath(node['node'][0][0], node['node'][0][1], start[0], start[1])
            closePoint = Path['closePoint']
            position = Open.index(node)
            if(len(Open) >= max_step or len(Close) == self.MAX_BRANCH):
                break
            elif(Path['path'] == []):
                if(position == end):
                    end = len(Open) - 1
                    deep += 1
                    print '    SEARCHING... ...', Type
                continue
            else:
                Zone = Windy.selectInPath(Path['path'], branches[deep])
                Selected = Zone['Selected']
                Cursor = Zone['Cursor']
                if(closePoint != []):
                    Selected.append(closePoint[0 : 2])
                    Cursor.append(closePoint[2])
                length = len(Cursor)
                for i in range(length):
                    nextLayer = self.switchLayer(Type, 0.9, 0.1)
                    Open.append(
                        {
                            'pre': position,
                            'cursor': Cursor[i],
                            'type': Type,
                            'node': [
                                Selected[i][0 : 2],
                                Windy.distance(Selected[i][0], Selected[i][1], start[0], start[1])
                            ],
                            'next': nextLayer
                        }
                    )
                    if(position == end and i == length - 1):
                        end = len(Open) - 1
                        deep += 1
                        print '    SEARCHING... ...',nextLayer
        Nodes = self.pooling(Open, pNumb * 3, 3)
        Path = self.rebuild(Nodes, Open)
        return Nodes, Path

    def search_land_loop(self, start, destiny, Node, pre_path):
        print 'SEARCHING PATH:', start, 'to', destiny
        print  '  STR In ',time.asctime(time.localtime(time.time()))
        end, deep = 0, 0
        NODES = [
            {
                'pre': 0,
                'cursor': 0,
                'type': Node['type'],
                'node': Node['node'],
                'next': Node['next']
            }
        ]
        for node in NODES:
            Type = node['next']
            Windy = self.WINDY[Type]
            Path = Windy.evolvePath(node['node'][0][0], node['node'][0][1], start[0], start[1], True, 50)
            closePoint = Path['closePoint']
            position = NODES.index(node)
            if(Type == '10mab'):
                break
            elif(Path['path'] == []):
                if(position == end):
                    end = len(NODES) - 1
                    deep += 1
                continue
            else:
                Zone = Windy.selectInPath(Path['path'], 1)
                Selected = Zone['Selected']
                Cursor = Zone['Cursor']
                if(closePoint != [] and deep <= 2):
                    Selected.append(closePoint[0 : 2])
                    Cursor.append(closePoint[2])
                length = len(Cursor)
                for i in range(length):
                    nextLayer = self.switchLayer(Type, 1, 0)
                    NODES.append(
                        {
                            'pre': position,
                            'cursor': Cursor[i],
                            'type': Type,
                            'node': [
                                Selected[i][0 : 2],
                                Windy.distance(Selected[i][0], Selected[i][1], start[0], start[1])
                            ],
                            'next': nextLayer
                        }
                    )
                    if(position == end and i == length - 1):
                        end = len(NODES) - 1
                        deep += 1
                        print '    SEARCHING... ...', nextLayer
        # Nodes = self.pooling(NODES, 1)
        Nodes = NODES[-1 : ]
        land_path = self.rebuild(Nodes, NODES)
        Path = pre_path + land_path
        return Nodes, Path

    def rebuild(self, Nodes, Open):
        Path = []
        # branches = len(Nodes)
        for node in Nodes[ : ]:
            path = []
            # distance = node['node'][1]
            while(True):
                pre = node['pre']
                preNode = Open[pre]['node']
                Type = node['type']
                clip = node['cursor']
                p = self.WINDY[Type].evolvePath(preNode[0][0], preNode[0][1])['path']
                path = p[ : clip] + path
                if(clip == pre == 0):
                    break
                else:
                    node = Open[pre]
            Path.append(path)
        print '  End In:', time.asctime(time.localtime(time.time()))
        return Path

    def pooling(self, List, branches, step = 1):
        Result = sorted(List, key= lambda i: i['node'][1])
        return Result[ : branches : step]

    def hierarchical_searche(self, start, destiny, branches):
        result = []
        # turn = 0
        Nodes, Path = self.search_path_loop(start, destiny, '250mb', 6800, branches[0], 5)
        # while(True):
        deep = 0
        end = len(Nodes) - 1
        for Node in Nodes:
            position = Nodes.index(Node)
            Type = Node['next']
            if(deep >= 2):
                break
            elif(
                    Node['node'][1] <= self.MIN_ZONE
                    and Node['type'] == self.data_type[0]
            ):
                if(position == end):
                    end = len(Nodes) - 1
                    deep += 1
                continue
            else:
                fPath = Path[position][ : ]
                nodes, path = self.search_path_loop(start, Node['node'][0], Type, 4500, branches[deep],5)
                length = len(nodes)
                for i in range(length):
                    splice_path = fPath + path[i]
                    Path.append(splice_path)
                    Nodes.append(nodes[i])
                    if(position == end and i == length - 1):
                        end = len(Nodes) - 1
                        deep += 1
        pool = self.pooling(Nodes, 20, 2)
        Nodes = pool
        for point in pool:
            pos = Nodes.index(point)
            path = Path[pos]
            result.append(
                {
                    'distance': point['node'][1],
                    'path': path
                }
            )
        return result
        # p = []
        #     p.append(path)
        # if(turn == 3):
        #     for n in Nodes:
        #         if(n['type'] == self.data_type[0]):
        #             pos = Nodes.index(n)
        #             path = Path[pos]
        #             result.append(
        #                 {
        #                     'distance': n['node'][1],
        #                     'path': path
        #                 }
        #             )
        #     break
        # Path = p
        # turn += 1
        # return result
                # print ''
                # n, p = self.search_land_loop(start, destiny, point, path)
