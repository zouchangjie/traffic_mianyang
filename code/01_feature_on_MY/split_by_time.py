'''
函数功能：用来从卡口数据中抽取某个特定时间段的数据
输入：卡口数据
输出：某一时间段的数据
'''
import pandas as pd

# 00_data/Traffic_flow/KAKOU201809.csv
reader = pd.read_csv('../00_data/Traffic_flow/KAKOU201809.csv', iterator=True, header=None, encoding="gb2312",
                     low_memory=False)  # 分块读取
chunkSize = 1000000  # 一次读取记录条数
chunks8 = []
# chunks9 = []
while True:
    try:
        chunk = reader.get_chunk(chunkSize)  # 一次获得1kw的数据量
        chunk[5] = pd.to_datetime(chunk[5])
        chunk1 = chunk[("2018/9/1 7:00:00" <= chunk[5]) & (chunk[5] < "2018/9/1 9:00:00")]
        # chunk9 = chunk[("2018/9/9 00:00:00" <= chunk[5]) & (chunk[5] < "2018/9/10 00:00:00")]

        chunks8.append(chunk1)
        # chunks9.append(chunk9)

    except StopIteration:
        print("Iteration is stopped.")
        break

df = pd.concat(chunks8, ignore_index=True)
df.to_csv('../00_data/Traffic_flow/1day7H9H.csv', header=None, index=None)

# df = pd.concat(chunks9, ignore_index=True)
# df.to_csv('./Data/9days.csv', header=None)
