#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/11/8 下午3:34
# @Author  : houlinjie
# @Site    :
# @File    : parse_file.py
# @Software: PyCharm

import os


src_file = open('./test.tsv', 'r')
save_file = open('./predict', 'a+')
for line in src_file.readlines():
    url = line.strip('\n').split()
    # url = line.split()
    print(type(url[1]))
    url[5] = '202000000100'
    # filename = url.split('/')[-1]
    # print(filename)
    print(url)
    save_file.write('{}\t{}\t{}\t{}\t{}\t{}\n'.format(url[0], url[1], url[2], url[3], url[4], url[5]))
