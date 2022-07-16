#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/11/6 下午3:53
# @Author  : houlinjie
# @Site    : 
# @File    : multiprocess_write_file.py
# @Software: PyCharm


# 把多个文件集中起来写入一个文件，就是把进程需要写入文件的内容作为返回值给回调函数，使用回调函数向文件中写入内容
# apply_async(func [])
# apply() 方法的一个变体，它返回一个结果对象
# 如果指定callback， 那么

import csv
from multiprocessing import Pool
import datetime

def mycallback(x):
    print(x)
    csv_write.writerow(x)

def sayHi(num):
    w = [str(num), str(num+1), str(num+2)]
    return w

if __name__ == "__main__":
    e1 = datetime.datetime.now()
    csv_file = open('Text.csv', 'w')
    csv_write = csv.writer(csv_file)
    p = Pool(4)
    for i in range(10):
        p.apply_async(sayHi, (i,), callback=mycallback)
    p.close()
    p.join()
    e2 = datetime.datetime.now()
    print((e2 - e1))
    csv_file.close()
