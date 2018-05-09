import os
import pandas as pd

# 以下变量用于合法性检查，暂时无用
ROOTPATH = './oceandata/'
RESULATION_DEFAULT = '0p083'  # 默认分辨率
ATTR_DEFAULT_1 = 'ssh'  # 默认海洋属性1 ssh
ATTR_DEFAULT_2 = 'temp'  # 默认海洋属性2 temp
TIME_DEFAULT = '2000-01-16'  # 默认时间
DEPTH_DEFAULT = '5p01m'  # 默认深度
DEPTH_LIST = ['0.0m', '8.0m', '15.0m', '30.0m', '50.0m']
ATTR_LIST = ['ssh', 'salinity', 'water_temp', 'water_u', 'water_v']

def get_data_heatmap(request):
    '''
    request.json是个dict, 下面是个例子
    {
        "resulation": 0p083,
        "attr": "ssh",
        "time": "2000-01-16",
        (option)"depth": "5p01m"
    }
    '''
    dataInfo = request.json
    # todo: dataInfo合法性检查
    path = ROOTPATH + dataInfo["resulation"]
    # 下面的filename还没有csv后缀
    fileName = '/'.join([path, dataInfo["attr"],
                         dataInfo["time"]])

    if 'depth' in dataInfo["file1"]:
        fileName += (',' + dataInfo["depth"] + '.csv')
    else:
        fileName += '.csv'

    df = pd.read_csv(fileName)
    df.columns = ['lon', 'lat', 'value']  # 这句其实有点多此一举
    # return pd.read_csv(fileName).to_json(orient='records')
    return df.to_json(orient='records')


def get_data_scatter(request):
    '''
    request.json是个dict, 下面是个例子
    {
        "resulation": 0p083, # 两文件的分辨率必须一致，其他不作要求
        "file1": {
            "attr": "ssh",
            "time": "2000-01-16",
            (option)"depth": "5p01m"
        }, # x
        "file2":{
            ...
        } # y
    }
    '''
    dataInfo = request.json
    # todo: dataInfo合法性检查
    path = ROOTPATH + dataInfo["resulation"]
    # 下面的filename还没有csv后缀
    fileName1 = '/'.join([path, dataInfo["file1"]["attr"],
                          dataInfo["file1"]["time"]])
    fileName2 = '/'.join([path, dataInfo["file2"]["attr"],
                          dataInfo["file2"]["time"]])

    # 根据需要加入后缀
    if 'depth' in dataInfo["file1"]:
        fileName1 += (',' + dataInfo["file1"]["depth"] + '.csv')
    else:
        fileName1 += '.csv'

    if 'depth' in dataInfo["file2"]:
        fileName2 += (',' + dataInfo["file2"]["depth"] + '.csv')
    else:
        fileName2 += '.csv'

    df1 = pd.read_csv(fileName1)
    df2 = pd.read_csv(fileName2)
    df3 = pd.merge(df1, df2, how='inner', on=['lon', 'lat'])
    df3.columns = ['lon', 'lat', 'x', 'y']
    # 不需要经纬度
    return df3.drop(columns=['lon', 'lat']).to_json(orient='records')


def get_data_paraller(request):
    '''
    request.json是个dict, 下面是个例子
    {
        "resulation": "0p2",
        "time":"2001-01-16",
        "depth":"5.01m",
        "attrs": ["ssh", "salt", ...]
    }
    '''
    dataInfo = request.json
    print(dataInfo)
    # todo: dataInfo合法性检查
    path = ROOTPATH + dataInfo["resulation"]

    # 最多返回6个可变属性的数据
    count = len(dataInfo["attrs"]) if 6 > len(dataInfo["attrs"]) else 6
    columns = ['lon', 'lat']
    for i in range(count):
        fileName = '/'.join([path, dataInfo["attrs"][i], dataInfo["time"]])
        print(fileName)
        if dataInfo["attrs"][i] != 'ssh':
            fileName += (',' + dataInfo["depth"] + '.csv')
        else:
            fileName += '.csv'

        columns.append(dataInfo["attrs"][i])
        df1 = pd.read_csv(fileName)
        if i != 0:
            df2 = pd.merge(df2, df1, how='inner', on=['lon', 'lat']) # ide会提示错误，确实很危险
        else:
            df2 = df1.copy()

    df2.columns = columns
    # 不需要经纬度
    return df2.drop(columns=['lon', 'lat']).to_json(orient='records')


def get_data_bylonlat(request):
    '''
    request.json是个dict，下面是个例子
    {
        "lon": 128.80,
        "lat": 32.88
    }
    '''
    dataInfo = request.json
    res = []
    for depth in DEPTH_LIST:
        absPath = '/'.join([ROOTPATH, depth])
        fileList = os.listdir(absPath)
        for file in fileList:
            if file[-4:] == '.csv':
                dict1 = {}
                df1 = pd.read_csv('/'.join([absPath, file]))
                queryExpr = 'lon=={0} and lat=={1}'.format(dataInfo['lon'], dataInfo['lat'])
                qdf = df1.query(queryExpr).drop(columns=['lon', 'lat'])
                dict1 = qdf.to_dict('record')
                dict1[0]['date'] = file[:-4]
                dict1[0]['depth'] = depth
                res.append(dict1)
    return jsonify(res)


def test(attr):
    path = ROOTPATH + attr
    print(path)
    return(path)


print(test('ssh'))
