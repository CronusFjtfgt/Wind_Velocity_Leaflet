from Windy import *

data_path = '../JSON/'
DATA = {
    '250mb': data_path + '2019050706.json',
    '10m': data_path + '2019050706_10m.json'
}

GRID = {}
WINDY = {}

for i in DATA.keys():
    with open(DATA[i], 'r') as d:
        data = json.load(d)
        WINDY[i] = Windy(data)

print WINDY['10m'].evolvePath(39, 112, 50, 200)
print WINDY['250mb'].evolvePath(39, 112, 50, 200)
