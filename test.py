#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/11/15 下午12:14
# @Author  : houlinjie
# @Site    : 
# @File    : test.py
# @Software: PyCharm


import os

url = '/rent-house-1/bcbf3ee35c303e0cc9799978d7cda7ff-1535231196065/efbc84569713d32bd68946f874f26716'
try:
    subfix = url.split('/')[-1].rsplit('.', 1)[1]
except Exception as e:
    subfix = 'jpg'
print(subfix)