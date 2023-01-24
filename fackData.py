import datetime
import os
import random
import numpy as np
import pandas as pd

def generator():
    while True:
        pf = pd.read_csv("fack.csv")
        for i in range(0, len(pf), 288):
            yield pf["cnt"].values.tolist()

def fack():
    begin_date = input("输入开始时间：")
    end_date = input("输入结束时间：")

    begin_date = datetime.datetime.strptime(begin_date, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    i = 0
    for y in generator():
        date_str = begin_date.strftime("%Y-%m-%d")
        x = []
        for h in range(24):
            for m in range(0, 60, 5):
                x.append(str(h) + ':' + str(m))

        i += 1
        with open(os.path.join("dayLogs", str(begin_date)[:10]+".txt"), "w", encoding='utf-8') as f:
            for i in range(288):
                f.write(str(y[i]))
                f.write("\t")
                f.write(x[i])
                f.write('\n')
        begin_date += datetime.timedelta(days=1)
        if begin_date > end_date:
            break

if __name__ == "__main__":
    fack()
