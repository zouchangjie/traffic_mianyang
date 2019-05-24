import pandas as pd

'''
函数功能：找出设备的下一个路口
需要文件：道路文件，设备文件
输出文件：新的设备文件
'''
equidata = pd.read_excel('../../Data/01_Original_data/00_equidata.xlsx', dtype=object, sep=',')
rodadata = pd.read_excel('../../Data/01_Original_data/00_roaddata.xlsx')

equidata['CROSS_ID_1'] = None
for i in range(len(equidata)):
    for j in range(len(rodadata)):
        if pd.isnull(equidata.iloc[i, 4]) or pd.isnull(equidata.iloc[i, 2]) or pd.isnull(
                rodadata.iloc[j, 5]) or pd.isnull(rodadata.iloc[j, 3]):
            pass
            # 为空
        elif int(equidata.iloc[i, 4]) == int(rodadata.iloc[j, 5]) and int(equidata.iloc[i, 2]) == int(
                rodadata.iloc[j, 3]):
            # 成功找到
            equidata.iloc[i, 5] = rodadata.iloc[j, 7]
            break

equidata.to_csv('../../Data/01_Original_data/out/01_equi_nextLukou.csv', encoding="GB2312")
print("以完成设备与下一个路口的匹配")
