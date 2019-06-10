# -*- coding: UTF-8 -*-

import math
import random

class Windy:
    '单风层数据类'

    MIN_VELOCITY_SPEED = 0.2 # 最低风速m/s
    EVOLVE_STEP = 2000 # 路径进化限制
    SEARCH_ZONE = 4.5 # 随机取点范围,约500km
    SCALE = 30*60 # 风速保持时间 30 min = 30*60 sec
    AWAY_PERMMIT_DISTANCE = 5 # 允许路径背离度数
    DISTANCE_TYPE = 'Euclidean' # 'Manhattan' #欧式距离和曼哈顿距离
    Data = []
    Grid = []
    LAYER_TYPE = ''

    lo1 = la1 = dy = dx = nx = ny = 0

    def __init__(self, DATA, type):
        self.Data = DATA
        self.LAYER_TYPE = type
        self.Grid = self.__buildGrid(self.Data)

    '======================================== PRIVATE ==============================='
    def __createBuilder(self, data):
        uComp = vComp = scalar = {}
        for record in data:
            parCategory = str(record['header']['parameterCategory'])
            parNumber = str(record['header']['parameterNumber'])
            case = parCategory + ',' + parNumber
            if(case == '1,2' or case == '2,2'):
                uComp = record
            elif(case == '1,3' or case == '2,3'):
                vComp = record
            else:
                scalar = record
        return self.__createWindBuilder(uComp, vComp)

    def __createWindBuilder(self, uComp, vComp):
        uData = uComp['data']
        vData = vComp['data']
        data = []

        for i in range(max(len(uData), len(vData))):
            data.insert(i, [uData[i], vData[i]])
        return {
            'header': uComp['header'],
            'data': data,
            'interpolate': self.__bilinearInterpolateVector
        }

    def __bilinearInterpolateVector(self, x, y, g00, g10, g01, g11):
        rx = 1 - x; ry = 1 - y
        a = rx * ry; b = x * ry; c = rx * y; d = x * y
        u = g00[0] * a + g10[0] * b + g01[0] * c +g11[0] *d
        v = g00[1] * a + g10[1] * b + g01[1] * c +g11[1] *d
        m = math.sqrt(u * u + v * v)
        return [u, v, m]

    def __buildGrid(self, data):
        builder = self.__createBuilder(data)
        header = builder['header']
        self.lo1 = header['lo1']
        self.la1 = header['la1']
        self.dy = header['dy']
        self.dx = header['dx']
        self.nx = header['nx']
        self.ny = header['ny']

        isContinuous = math.floor(self.nx * self.dx) >= 360
        grid = []
        p = 0
        for j in range(self.ny):
            row = []
            for i in range(self.nx):
                row.insert(i, builder['data'][p])
                p +=1
            if(isContinuous):
                row.append(row[0])
                grid.insert(j, row)
        return grid

    def __interpolateField(self):
        projection = {}
        columns = []
        pass

    def __interpolate(self, lat, lng):
        if(self.Grid == []):
            return
        dlng = lng - self.lo1
        i = (dlng - math.floor(dlng / 360) * 360) /self.dx
        j = (self.la1 - lat) / self.dy
        fi = int(math.floor(i)); ci = fi + 1
        fj = int(math.floor(j)); cj = fj + 1

        if(self.Grid[fj]):
            row = self.Grid[fj]
            g00 = row[fi]; g10 = row[ci]
            if(g00 and g10 and self.Grid[cj]):
                row = self.Grid[cj]
                g01 = row[fi]
                g11 = row[ci]
                if(g01 and g11):
                    return self.__bilinearInterpolateVector(
                        i - fi,
                        j - fj,
                        g00, g10, g01, g11
                    )
        return

    def __field(self, lat, lng):
        ''''大地坐标系资料WGS-84
            长半径a=6378137 短半径b=6356752.3142 扁率f=1/298.2572236
            地球周长40075016m
        '''
        a = 6378137
        b = 6356752.3142
        avgR = 6371229
        f = 1 / 298.2572236
        pi = math.pi
        distance = self.__interpolate(lat, lng)
        # disX = distance[0]; disY = distance[1] # 正向路径
        disX =  -distance[0]; disY = -distance[1] #反向路径
        #================================ 平均半径计算 ==========================
        degree = self.deg2rad(avgR)
        dLat = (disY / degree) * self.SCALE + lat
        dLng = (disX / (degree * math.cos(self.deg2rad(lat)))) * self.SCALE + lng
        #================================ 长短半径分开计算 ==========================
        # degreeLat = b * pi / 180
        # degreeLng = a * pi / 180
        # dLat = (disY / degreeLat) * self.scale + lat
        # dLng = (disX / (degreeLng * math.cos(self.deg2rad(lat)))) * self.scale + lng

        return [dLat, dLng, distance[2], self.LAYER_TYPE]

    def __isInZone(self, center, point):
        min_lat = center[0] - self.SEARCH_ZONE
        min_lng = center[1] - self.SEARCH_ZONE
        max_lat = center[0] + self.SEARCH_ZONE
        max_lng = center[1] + self.SEARCH_ZONE
        if(min_lat <= point[0] and max_lat >= point[0] and min_lng <= point[1] and max_lng >= point[1]):
            return True
        else:
            return False

    '======================================== PUBLIC ==============================='
    def distance(self, lat, lng, dLat, dLng):
        if(self.DISTANCE_TYPE == 'Euclidean'):
            x = dLat - lat; y = dLng - lng
            return math.hypot(x, y)
        elif(self.DISTANCE_TYPE == 'Manhattan'):
            x = math.fabs(dLat - lat)
            y = math.fabs(dLng - lng)
            return x+y

    def deg2rad(self, deg):
        return deg / 180 * math.pi

    def rad2deg(self, rad):
        return rad / (math.pi / 180)

    def evolvePath(self, lat, lng, deslat = -1, deslng = -1):

        path = []
        closePoint = []

        guilder = [lat, lng, self.__interpolate(lat, lng)[2], self.LAYER_TYPE]
        min_distance = self.distance(guilder[0], guilder[1], deslat, deslng)
        cursor = 0
        while(guilder[2] >= self.MIN_VELOCITY_SPEED and cursor <= self.EVOLVE_STEP):
            path.append(guilder)
            # print guilder
            cursor += 1
            if(deslat != -1 and deslng != -1):
                cur_distance = self.distance(guilder[0], guilder[1], deslat, deslng)
                if(cur_distance < min_distance):
                    min_distance = cur_distance
                    closePoint = [guilder[0], guilder[1], cursor, min_distance]
                elif(math.fabs(cur_distance - min_distance) >= self.AWAY_PERMMIT_DISTANCE):
                    break
            guilder = self.__field(guilder[0], guilder[1])
        return {
            'path': path,
            'closePoint': closePoint
        }

    def selectInPath(self, path, pointNumber):
        if(path):
            selected = []
            cursor = []
            while(len(selected) < pointNumber):
                p = random.choice(path)
                if(p not in selected):
                    cursor.append(path.index(p))
                    selected.append(p)
            return {
                'Selected': selected,
                'Cursor': cursor
            }
        else:
            return

    def selectInZone(self, path, closePoint, pointNumber):
        if(closePoint[2] == 0):
            i = 0; j = 1
        elif(closePoint[2] == len(path) - 1):
            j = len(path) - 1; i = j -1
        else:
            i = closePoint[2] - 1
            j = closePoint[2] + 1
        center = closePoint[:2]
        j_finish = i_finish = 0
        while(True):
            if(i> 0 and self.__isInZone(center, path[i])):
                i -= 1
            else:
                i_finish = 1
            if(j<len(path) and self.__isInZone(center, path[j])):
                j += 1
            else:
                j_finish = 1
            if(i_finish and j_finish):
                break
        zone = path[i: j+1]
        selected = []
        cursor = []
        while(len(selected) < pointNumber):
            p = random.choice(zone)
            if(p not in selected):
                cursor.append(zone.index(p) + i)
                selected.append(p)
        return {
            'Selected': selected,
            'Cursor': cursor
        }

    def clearPartWind(self, top, left, bottom, right):
        y1 = int(math.ceil((self.la1 - top)/self.dy)); x1 = int(math.floor(left/self.dx))
        y2 = int(math.floor((self.la1 - bottom)/self.dy)); x2 = int(math.ceil(right/self.dx))
        print [y1,x1],[y2,x2]
        for j in range(y2 - y1):
            for i in range(x2 - x1):
                self.Grid[y1 + j][x1 + i] = [0, 0]
        return True







