# -*- coding: UTF-8 -*-

from Windy import *

class GlobalWindy:
    '多风层数据类'

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
    destiny = [50, 200]

    def __init__(self):
        for i in range(len(self.data_name)):
            type = self.data_type[i]
            self.DATA[type] = self.data_path + self.data_name[i]
            with open(self.DATA[type], 'r') as d:
                data = json.load(d)
                self.WINDY[type] = Windy(data)
                print 'Load:',type
        distance = self.WINDY['10m'].distance(self.start[0], self.start[1], self.destiny[0], self.destiny[1])
        dis = self.searchPath(self.start, self.destiny, '10m', distance)
        print dis
        # wind = self.WINDY['10m']
        # Path = wind.evolvePath(self.start[0], self.start[1], self.destiny[0], self.destiny[1])
        # selected =  wind.searchZone(Path['path'], Path['closePoint'], 2)
        # print selected

    def switchLayer(self, layerType):
        layer_numb = self.data_type.index(layerType)
        if(layer_numb == 0):
            nextLayer = layer_numb + 1
        else:
            nextLayer = layer_numb + random.choice([-1, 1])
        return self.data_type[nextLayer]

    def searchPath(self, start, destiny, type, distance):
        Windy = self.WINDY[type]
        Path = Windy.evolvePath(start[0], start[1], destiny[0], destiny[1])
        if(Path['closePoint'] == [] or Path['closePoint'][3] == distance):
            return float('inf')
        elif(Path['closePoint'][3] < 2):
            return Path['closePoint'][3]
        else:
            dis = []
            Selected = Windy.searchZone(Path['path'], Path['closePoint'], 2)
            for point in Selected:
                print type,' point:',point
                dis.append(
                    self.searchPath(
                        point, destiny, self.switchLayer(type),
                        Windy.distance(point[0], point[1], destiny[0], destiny[1])
                    )
                )
            return min(dis)

