#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/11/27 下午12:50
# @Author  : houlinjie
# @Site    : 
# @File    : encode_jpg.py
# @Software: PyCharm
import cv2

img = cv2.imread('test.png')
img_encode = cv2.imencode('.jpg', img)[1]
