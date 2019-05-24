import pandas as pd
from math import radians, cos, sin, asin, sqrt

"""
函数功能：计算两个坐标点之间的距离
函数输入：两个坐标点
函数输出：距离（单位m）
"""


def geodistance(Piont1, Piont2):
    # 经度，纬度
    lng1, lat1, lng2, lat2 = map(radians,
                                 [float(Piont1[0]), float(Piont1[1]), float(Piont2[0]), float(Piont2[1])])  # 经纬度转换成弧度
    dlon = lng2 - lng1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    distance = 2 * asin(sqrt(a)) * 6371 * 1000  # 地球平均半径，6371km
    # distance 距离单位为米(m)
    return round(distance, 3)


"""
函数功能：将涪城区的路网数据，变得规整
对kml路口和绵阳路口一一匹配，并对有设备的路口进行标记

原始文件："00_涪城区_矢量路网.kml" 用vs MutiIRL 截取所有经纬度
注意，有些经纬度 中间有<LineString><coordinates> 要把它替换成空格

输入：涪城区路网信息01_FuCheng_RoadNet（由kml文件所得）（m列*n行，数据不规整）
函数输入：设备文件，绵阳路口文件，kml路网文件

输出：规整的涪城区路网数据02_FuCheng_RoadNet_Nx4 （【N行4列】,两点之间用‘,’分隔）
函数输出：kml路口文件，该文件对kml路口进行了标号，找到了与kml路口对应的绵阳路口，并标记了是否有设备
"""


# 第一步路网与节点（原始路网与节点）
def MarkkmlbySBBM():
    # 规整Kml的路网
    file = open('../../Data/01_Original_data/00_FuCheng_RoadNet.txt')
    out = open('../../Data/02_RoadNet/temp/00_KmlRoadNet.csv', "w")
    flag = 0
    for line in file.readlines():
        curLine = line.strip().split(" ")
        if len(curLine) > 2:
            for i in range(len(curLine) - 1):
                temp = [curLine[i], curLine[i + 1]]

                flag = flag + 1
                out.write(str(temp[0]) + ',' + str(temp[1]) + "\n")
        else:
            flag = flag + 1

            out.write(str(curLine[0]) + ',' + str(curLine[1]) + "\n")
    # print("完成第一步：\n规整路网,输出文件为涪城区路网信息【N行4列】文件名为00_KmlRoadNet")

    # 根据Kml的路网，整理路口
    KmlRoadNet = pd.read_csv('../../Data/02_RoadNet/temp/00_KmlRoadNet.csv', header=None, dtype=object)

    KmlRoadNet = KmlRoadNet.astype(float).round(7)
    KmlNode = pd.DataFrame(columns=[0, 1])
    KmlNode[0] = pd.concat([KmlRoadNet[0], KmlRoadNet[2]], names=[0])
    KmlNode[1] = pd.concat([KmlRoadNet[1], KmlRoadNet[3]], names=[1])

    KmlNode = KmlNode.drop_duplicates([0, 1])
    KmlNode = KmlNode.reset_index(drop=True)
    KmlNode = KmlNode.reset_index()
    KmlNode.columns = ['KmlID', 'LONGITUDE', 'LATITUDE']

    KmlNode['MYID'] = None
    KmlNode['SBBMNUM'] = 0

    # 将绵阳路口和设备进行匹配
    SBBM = pd.read_excel('../../Data/01_Original_data/00_equidata.xlsx', dtype=object)
    MyNode = pd.read_excel('../../Data/01_Original_data/00_MyNode.xlsx', dtype=object)
    MyNode['SBBMNUM'] = 0
    for i in range(len(SBBM)):
        CROSS_ID = SBBM.loc[i, 'CROSS_ID']
        MyNode.loc[MyNode['ID'] == CROSS_ID, 'SBBMNUM'] += 1
    MyNode['LONGITUDE'] = MyNode['LONGITUDE'].astype(float)
    MyNode['LATITUDE'] = MyNode['LATITUDE'].astype(float)

    exception = pd.DataFrame(columns=[0, 1, 2, 3])
    # 将kml路口和绵阳路口一一匹配，并对有设备的路口进行标记
    for i in range(len(MyNode)):
        # print('进度', i, len(MyNode))
        minDistance = 6371 * 1000  # 地球平均半径，6371km
        minindex = 10000
        MyPoint = [MyNode.loc[i, 'LONGITUDE'], MyNode.loc[i, 'LATITUDE']]
        for j in range(len(KmlNode)):
            # if KmlNode.loc[j, 'MYID']:
            #     continue
            KmlPoint = [KmlNode.loc[j, 'LONGITUDE'], KmlNode.loc[j, 'LATITUDE']]
            distance = geodistance(MyPoint, KmlPoint)
            if distance < minDistance:
                minDistance = distance
                minindex = j

        if pd.isna(KmlNode.loc[minindex, 'MYID']):
            KmlNode.loc[minindex, 'MYID'] = MyNode.loc[i, 'ID']
            KmlNode.loc[minindex, 'SBBMNUM'] = MyNode.loc[i, 'SBBMNUM']

        elif KmlNode.loc[minindex, 'SBBMNUM'] == 0:
            KmlNode.loc[minindex, 'MYID'] = MyNode.loc[i, 'ID']
            KmlNode.loc[minindex, 'SBBMNUM'] = MyNode.loc[i, 'SBBMNUM']

        elif KmlNode.loc[minindex, 'SBBMNUM'] > 0 and MyNode.loc[i, 'SBBMNUM'] > 0:
            # print(KmlNode.loc[minindex, 'MYID'], KmlNode.loc[minindex, 'SBBMNUM'],
            #       MyNode.loc[i, 'ID'], MyNode.loc[i, 'SBBMNUM'])

            tempexception = pd.DataFrame(
                {0: KmlNode.loc[minindex, 'MYID'],
                 1: KmlNode.loc[minindex, 'SBBMNUM'],
                 2: MyNode.loc[i, 'ID'],
                 3: MyNode.loc[i, 'SBBMNUM']},
                pd.Index(range(1))
            )
            exception = exception.append(tempexception, ignore_index=True)
    # exception.reset_index(drop=True,inplace=True)
    exception.to_csv("../../Data/02_RoadNet/temp/01_exceptionMyID.csv", index=None, header=None)
    KmlRoadNet.to_csv("../../Data/02_RoadNet/temp/01_KmlRoadNet.csv", index=None, header=None)
    KmlNode.to_csv("../../Data/02_RoadNet/temp/01_KmlNode.csv", index=None)
    print("第一步：完成匹配")


"""
切割路网：
输入数据：RoadNode

旧切割路网范围：
纬度：31.435~31.513 
北取龙溪物流园  104.717637,31.513032
南取绵阳南郊机场  104.749689,31.435669

经度：104.60 ~ 104.774
东磨家枢纽 104.603876,31.450148
西青年广场 104.774194,31.46093


新的切割下限104.60142,31.440409
输出：切割后的点集
"""


def split_RoafNet():
    KmlNode = pd.read_csv('../../Data/02_RoadNet/temp/01_KmlNode.csv', dtype=object, index_col=['KmlID'])
    df = KmlNode.astype(float)
    # kmlLine = kmlLine.astype(int)
    for i in range(len(df)):
        # 判断节点
        if (df.loc[i, 'LONGITUDE'] <= 104.774194 and df.loc[i, 'LONGITUDE'] >= 104.60 and \
                df.loc[i, 'LATITUDE'] <= 31.513032 and df.loc[i, 'LATITUDE'] >= 31.40):
            pass
        else:
            df = df.drop(i, axis=0)

    df = df.reset_index(drop=True)

    df.to_csv('../../Data/02_RoadNet/temp/02_KmlNode.csv', index_label=['KmlID'])
    print("第二步：完成切割")
    return 0


"""
函数功能：清洗路网中多余的节点
比如 1---2---3，如果2没有其他分支，那么就删除
输入：规整的涪城区路网数据 （2列*n行）
输出：删除掉多余节点的路网数据
"""


def isHaveSBBM(i):
    flag = False
    df_node = pd.read_csv("../../Data/02_RoadNet/temp/02_KmlNode.csv", dtype=object, index_col=['KmlID'])
    df_node['xy'] = df_node['LONGITUDE'].str.cat(df_node['LATITUDE'], sep=',')

    nodeIndexlist = df_node.loc[df_node['xy'] == i, 'MYID'].index
    if len(nodeIndexlist) > 0:
        # print(len(nodeIndexlist))
        nodeIndex = nodeIndexlist[0]

        if not pd.isna(df_node.loc[nodeIndex, 'MYID']):
            flag = True

    return flag


def clean_node():
    df_node = pd.read_csv("../../Data/02_RoadNet/temp/02_KmlNode.csv", dtype=object, index_col=['KmlID'])
    df_node['xy'] = df_node['LONGITUDE'].str.cat(df_node['LATITUDE'], sep=',')

    df_data = pd.read_csv("../../Data/02_RoadNet/temp/00_KmlRoadNet.csv", header=None, dtype=object)

    df_data = df_data.astype(float).round(7).astype(str)
    df1 = pd.DataFrame(columns=[0, 1])
    df1[0] = df_data[0].str.cat(df_data[1], sep=',')
    df1[1] = df_data[2].str.cat(df_data[3], sep=',')

    FLAG = True
    num = len(df1)
    while FLAG:
        FLAG = False
        a = set(df1[0])
        b = set(df1[1])
        allnode = a | b
        # print("allnode", len(allnode))
        for i in allnode:
            tampA = df1[df1[1] == i]
            tampB = df1[df1[0] == i]
            if len(tampA) == 1 and len(tampB) == 1 and tampA.index[0] != tampB.index[0]:
                # 判断该点是否匹配过路口，如果有就不删除
                if isHaveSBBM(i):
                    # print("跳过一个点")
                    continue
                FLAG = True
                newTemp = pd.DataFrame([[tampA.iloc[0, 0], tampB.iloc[0, 1]]], columns=[0, 1], index=[num])
                df1 = df1.append(newTemp)
                num = num + 1
                df1.drop(tampA.index[0], inplace=True)
                df1.drop(tampB.index[0], inplace=True)

    # print("allnode", len(allnode))
    # 根据路网反删节点
    df1.reset_index(drop=True, inplace=True)

    for i in range(len(df_node)):
        if df_node.loc[i, 'xy'] not in allnode:
            df_node.drop(i, inplace=True)
    df_node.reset_index(drop=True, inplace=True)
    df_node.drop('xy', axis=1, inplace=True)

    df_node.sort_values(['LATITUDE', 'LONGITUDE'], inplace=True)
    df_node = df_node.reset_index(drop=True)
    df_node.to_csv("../../Data/02_RoadNet/temp/03_KmlNode.csv", index_label=['KmlID'])

    df2 = pd.DataFrame(columns=[0, 1, 2, 3])
    df2[0] = df1[0].str.split(",").str[0]
    df2[1] = df1[0].str.split(",").str[1]
    df2[2] = df1[1].str.split(",").str[0]
    df2[3] = df1[1].str.split(",").str[1]
    df2.to_csv("../../Data/02_RoadNet/temp/03_KmlRoadNet.csv", header=None, index=None)
    print("完成第三步：清洗路网中多余的节点")

    return 0


"""
函数功能：合并相邻的点，距离为100米
"""
# a = [103.99302, 30.586034]
# b = [103.99252, 30.585556]
# Judge = geodistance(a,b)
Judge = 100


def judeDistance(Piont1, Piont2):
    global Judge
    Flag = False
    distance = geodistance(Piont1, Piont2)
    # print("distance", distance)
    if Judge >= distance:
        Flag = True
    return Flag


def get_NewPiont(Piont1, Piont2):
    Piont1 = [float(i) for i in Piont1]
    Piont2 = [float(i) for i in Piont2]
    newPiont = [(Piont1[0] + Piont2[0]) / 2.0, (Piont1[1] + Piont2[1]) / 2.0]
    # newPiont = Piont1

    newPiont = [round(i, 7) for i in newPiont]
    return newPiont


def group_kmlNode():
    Node_data = pd.read_csv("../../Data/02_RoadNet/temp/03_KmlNode.csv", dtype=object)
    Node_data = Node_data.astype(float).round(7)
    Node_data['newKmlID'] = Node_data['KmlID']
    Node_data['newLONGITUDE'] = Node_data['LONGITUDE']
    Node_data['newLATITUDE'] = Node_data['LATITUDE']
    flag = True
    temp_data = Node_data.drop_duplicates('newKmlID', keep='first')
    temp_data['newKmlID_1'] = None
    while flag:
        flag = False
        temp_data = temp_data.drop_duplicates('newKmlID', keep='first')

        # print("长度", len(temp_data))
        temp_data['newKmlID_1'] = temp_data['newKmlID']
        nodeID = set(temp_data['newKmlID_1'])
        nodeID = list(nodeID)
        nodeID.sort()
        temp_data = temp_data.set_index(['newKmlID_1'])
        for i in range(len(nodeID)):
            point1 = [temp_data.loc[nodeID[i], 'newLONGITUDE'], temp_data.loc[nodeID[i], 'newLATITUDE']]
            for j in range(len(nodeID)):
                if i == j:
                    break
                point2 = [temp_data.loc[nodeID[j], 'newLONGITUDE'], temp_data.loc[nodeID[j], 'newLATITUDE']]

                if judeDistance(point1, point2):

                    if temp_data.loc[nodeID[i], 'SBBMNUM'] > 0 and temp_data.loc[nodeID[j], 'SBBMNUM'] == 0:
                        flag = True
                        temp_data.loc[nodeID[j], 'newKmlID'] = temp_data.loc[nodeID[i], 'newKmlID']
                        [x, y] = get_NewPiont(point1, point2)
                        temp_data.loc[nodeID[i], 'newLONGITUDE'] = x
                        temp_data.loc[nodeID[i], 'newLATITUDE'] = y
                        temp_data.loc[nodeID[j], 'newLONGITUDE'] = x
                        temp_data.loc[nodeID[j], 'newLATITUDE'] = y

                    elif temp_data.loc[nodeID[i], 'SBBMNUM'] == 0 and temp_data.loc[nodeID[j], 'SBBMNUM'] > 0:
                        flag = True
                        temp_data.loc[nodeID[i], 'newKmlID'] = temp_data.loc[nodeID[j], 'newKmlID']
                        [x, y] = get_NewPiont(point1, point2)

                        temp_data.loc[nodeID[i], 'newLONGITUDE'] = x
                        temp_data.loc[nodeID[i], 'newLATITUDE'] = y
                        temp_data.loc[nodeID[j], 'newLONGITUDE'] = x
                        temp_data.loc[nodeID[j], 'newLATITUDE'] = y

                    elif temp_data.loc[nodeID[i], 'SBBMNUM'] == 0 and temp_data.loc[nodeID[j], 'SBBMNUM'] == 0:
                        flag = True
                        temp_data.loc[nodeID[j], 'newKmlID'] = temp_data.loc[nodeID[i], 'newKmlID']
                        [x, y] = get_NewPiont(point1, point2)

                        temp_data.loc[nodeID[i], 'newLONGITUDE'] = x
                        temp_data.loc[nodeID[i], 'newLATITUDE'] = y
                        temp_data.loc[nodeID[j], 'newLONGITUDE'] = x
                        temp_data.loc[nodeID[j], 'newLATITUDE'] = y

        for i in temp_data.index:
            index = temp_data.loc[i, 'KmlID']

            Node_data.loc[Node_data['KmlID'] == index, 'newKmlID'] = temp_data.loc[i, 'newKmlID']
            Node_data.loc[Node_data['KmlID'] == index, 'newLONGITUDE'] = temp_data.loc[i, 'newLONGITUDE']
            Node_data.loc[Node_data['KmlID'] == index, 'newLATITUDE'] = temp_data.loc[i, 'newLATITUDE']
            # print("替换", index, temp_data.loc[i, 'newKmlID'])

    # temp_data.to_csv("../../Data/02_RoadNet/temp/043_KmlNode.csv", )
    Node_data.to_csv("../../Data/02_RoadNet/temp/04_KmlNode.csv", index=None)
    # print("路网还有节点数", len(Node_data.drop_duplicates('newKmlID', keep='first')))
    global Judge

    print("完成第四步：融点距离为", Judge)
    return 0


def get_RoadNet():
    kmlNode = pd.read_csv("../../Data/02_RoadNet/temp/04_KmlNode.csv", index_col=['KmlID'])
    kmlLine = pd.read_csv("../../Data/02_RoadNet/temp/03_KmlRoadNet.csv", header=None)
    Node_data = kmlNode.copy()
    # 将一个文件两列合成一列
    kmlNode = kmlNode.astype(str)
    kmlNode['xy'] = kmlNode['LONGITUDE'].str.cat(kmlNode['LATITUDE'], sep='-')
    kmlNode.drop(['LONGITUDE', 'LATITUDE'], axis=1, inplace=True)

    # 四列合成两列
    kmlLine = kmlLine.astype(str)
    kmlLine['0'] = kmlLine[0].str.cat(kmlLine[1], sep='-')
    kmlLine['1'] = kmlLine[2].str.cat(kmlLine[3], sep='-')
    kmlLine = kmlLine[['0', '1']]

    kmlLine['start'] = -1
    kmlLine['end'] = -1

    for i in range(len(kmlLine)):
        point = kmlLine.loc[i, '0']
        a = kmlNode[kmlNode['xy'] == point]
        if len(a) > 0:
            index = a.index[0]
            kmlLine.loc[i, 'start'] = kmlNode.loc[index, 'newKmlID']

        point2 = kmlLine.loc[i, '1']
        b = kmlNode[kmlNode['xy'] == point2]
        if len(b) > 0:
            index2 = b.index[0]
            kmlLine.loc[i, 'end'] = kmlNode.loc[index2, 'newKmlID']

    kmlLine.drop('0', axis=1, inplace=True)
    kmlLine.drop('1', axis=1, inplace=True)
    kmlLine.drop(kmlLine[kmlLine['start'] == -1].index, inplace=True)
    kmlLine.drop(kmlLine[kmlLine['end'] == -1].index, inplace=True)

    kmlLine = kmlLine[['start', 'end']]
    kmlLine = kmlLine.astype(float).astype(int)

    # 删除起点 终点 一样的
    kmlLine.drop_duplicates(['start', 'end'], keep='first', inplace=True)
    for i in kmlLine.index:
        if kmlLine.loc[i]['start'] == kmlLine.loc[i]['end']:
            kmlLine.drop(i, inplace=True)

    Node_data = Node_data.astype(float).round(7)
    kmlLine.to_csv('../../Data/02_RoadNet/temp/05_KmlRoadNet.csv', index=None)
    Node_data.to_csv("../../Data/02_RoadNet/temp/05_KmlNode.csv")
    print("完成第五步：根据节点，重新命名路网")


def correct_RoadNet():
    Node = pd.read_csv("../../Data/02_RoadNet/temp/05_KmlNode.csv", dtype=object)
    kmlLine = pd.read_csv('../../Data/02_RoadNet/temp/05_KmlRoadNet.csv')
    Node["newKmlID"] = Node["newKmlID"].astype(float).astype(int)

    lineNode = set(kmlLine['start']) | set(kmlLine['end'])

    for i in range(len(Node)):
        if float(Node.loc[i, 'newKmlID']) not in lineNode:
            Node.drop(i, inplace=True)
            # print("路网中没有的节点",i)

    Node['TureKmlID'] = -1

    temp = list(set(Node['newKmlID']))
    temp.sort()

    for i in Node.index:
        a = temp.index(Node.loc[i, 'newKmlID'])
        Node.loc[i, 'TureKmlID'] = a

    Node = Node.sort_values('TureKmlID')

    for i in kmlLine.index:
        a = temp.index(kmlLine['start'][i])
        kmlLine['start'][i] = a
        b = temp.index(kmlLine['end'][i])
        kmlLine['end'][i] = b

    Node = Node.drop(['LONGITUDE', 'LATITUDE', 'newKmlID'], axis=1)

    kmlLine.sort_values(['start', 'end'], inplace=True)
    kmlLine.to_csv('../../Data/02_RoadNet/06_KmlRoadNet.csv', index=None)
    Node.to_csv("../../Data/02_RoadNet/temp/06_KmlNode.csv", index=None)
    print("完成第六步：根据路网修正节点，删除没有在路网中出现的点并重排")


def add_liwai():
    Node = pd.read_csv("../../Data/02_RoadNet/temp/06_KmlNode.csv", dtype=object, index_col=['KmlID'])
    sunshi = pd.read_csv("../../Data/02_RoadNet/temp/01_exceptionMyID.csv", header=None)
    Node['MYID'] = Node['MYID'].astype(float)

    MYID = set(Node['MYID'])
    for i in range(len(sunshi)):
        if sunshi.loc[i, 0] in MYID:
            print("替换")
            Node = Node.append(Node.loc[Node['MYID'] == sunshi.loc[i, 0]], ignore_index=True)
            Node.loc[len(Node) - 1, 'MYID'] = sunshi.loc[i, 2]
            Node.loc[len(Node) - 1, 'SBBMNUM'] = sunshi.loc[i, 3]

    Node.to_csv("../../Data/02_RoadNet/07_KmlNode.csv", index=None)
    print("完成第七步：补全缺失的几个绵阳路口")


if __name__ == '__main__':
    # # # 第一步：对点：进行匹配
    # MarkkmlbySBBM()
    # #
    # # # # 第二步：对点：切割地图
    # split_RoafNet()
    # #
    # # # # 第三步：对路网：删除度为2的点
    # clean_node()
    #
    # # # 第四步：融点（距离参数为100）
    # group_kmlNode()
    # #
    # # # # 第五步：根据点重新对路网进行编号
    # get_RoadNet()
    # #
    # # # # # 第六步：修整路网
    correct_RoadNet()

    # # 添加例外的MyID
    add_liwai()
