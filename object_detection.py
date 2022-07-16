#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/11/27 上午11:15
# @Author  : houlinjie
# @Site    : 
# @File    : object_detection.py
# @Software: PyCharm

from PIL import Image
import requests
import base64
import time
import argparse
# import tensorflow as tf
import os
from io import BytesIO, StringIO
import math
import logging

domain = 'http://image.media.lianjia.com'
DETECT_DOMAIN = "http://api.heimdallr.lianjia.com/v2/detect_furniture"
subfix = '!m_fit,w_300,h_300'
parser = argparse.ArgumentParser()

# parser.add_argument(
#     '--img_dir',
#     required=True,
#     type=str,
#     help='save image directory'
# )
# predict_result = open('predict_res.txt', 'a+')
# FLAGS, unparsed = parser.parse_known_args()
# for filename in os.listdir(FLAGS.img_dir):
#     try:
#         time_stamp = str(int(time.time() * 100))
#         request_id = time_stamp + ',' + 'd6a9aa03-84e4-4916-9e92-c65094b192d0'
#         im = Image.open(os.path.join(FLAGS.img_dir, filename))
#         jpg_im = im.convert('RGB')
#         img_jpg = os.path.splitext(filename)[0]
#         save_img = img_jpg + '.jpg'
#         jpg_im.save(save_img)
#         img_base64 = base64.b64encode(open(save_img, "rb").read())
#         data = {'request_id': request_id, 'img_base64': img_base64}
#         r = requests.post(DETECT_DOMAIN, data=data).json()
#     except Exception as e:
#         print(filename)
#         print(e)
#         continue
#     print(r)
#     predict_result.write('{}\t{}\n'.format(filename, r))

image_extention = ['jpg', 'JPG', 'JPEG', 'jpeg', 'png', 'PNG']
parser.add_argument(
    '--img_path',
    required=True,
    type=str,
    help='compute image path'
)


# def urllibopen(url, path, filename):
#     try:
#         sock = urllib.urlopen(url)
#         htmlcode = sock.read()
#         sock.close()
#         filedir = open(os.path.join(path, filename), 'wb')
#         filedir.write(htmlcode)
#         filedir.close()
#     except Exception as e:
#         logging.info('Url image open error: %s', err)
#
FLAGS, unparsed = parser.parse_known_args()
# time_stamp = str(int(time.time() * 100))
# request_id = time_stamp + ',' + 'd6a9aa03-84e4-4916-9e92-c65094b192d0'
# im = Image.open(FLAGS.img_path)
# jpg_im = im.convert('RGB')
# img_jpg = os.path.splitext(FLAGS.img_path)[0]
# save_img = img_jpg + '.jpg'
# jpg_im.save(save_img)
# shrink_time = time.time()
# url = domain + FLAGS.img_path + subfix
# s = requests.session()
# s.keep_alive = False
# response = s.get(url)
# global detect_set
# detect_set = []
# fd = BytesIO(response.content)
# image = Image.open(fd)
# scale_height = int(math.ceil((300 / float(image.size[0])) * image.size[1]))
# pic = image.resize((300, scale_height), Image.BICUBIC)
# img_filename = FLAGS.img_path.split('/')[-1]
# print(img_filename)
# try:
#     subfix = img_filename.rsplit('.', 1)[1]
#     if subfix in image_extention:
#         pic.save(img_filename)
#     else:
#         pass
# except Exception as e:
#     print(e)
#     img_filename = img_filename + '.jpg'
#     pic.save(img_filename)
# shrink_elapsed_time = time.time() - shrink_time
# print(shrink_elapsed_time)
# img_base64 = base64.b64encode(open(FLAGS.img_path, "rb").read())
# img_base64 = base64.b64encode(response.content)
# elapsed_time = time.time() - shrink_time
# print(elapsed_time)
# data = {'request_id': request_id, 'img_base64': img_base64}
# r = requests.post(DETECT_DOMAIN, data=data).json()
# if r['error_code'] == -1:
#     pass
# else:
#     if len(r['result']) == 0:
#         pass
#     else:
#         for i in range(len(r['result'])):
#             detect_set.append(r['result'][i]['label'])
# if 'toilet' in detect_set:
#     print(True)
# print(detect_set)


def detect_furniture_exists(img_path):
    furniture_list = ['televison', 'refrigerator', 'washing_machine', 'air_conditioner', 'water_heater', 'bed',
                      'radiator', 'wardrobe', 'gas_stove', 'desk', 'chair', 'sofa', 'range_hood', 'toilet', 'bunk_beds',
                      'loft_bed_with_desk']
    furniture_set = set(furniture_list)
    detect_list = []
    time_stamp = str(int(time.time() * 100))
    request_id = time_stamp + ',' + 'd6a9aa03-84e4-4916-9e92-c65094b192d0'
    url = domain + img_path
    try:
        s = requests.session()
        s.keep_alive = False
        response = s.get(url)
        img_base64 = base64.b64encode(response.content)
        # img_base64 = base64.b64encode(open(img_path, "rb").read())
        data = {'request_id': request_id, 'img_base64': img_base64}
        r = requests.post(DETECT_DOMAIN, data=data).json()
        print(r)
        if r['error_code'] == -1:
            pass
        else:
            if len(r['result']) == 0:
                pass
            else:
                for i in range(len(r['result'])):
                    detect_list.append(r['result'][i]['label'])
        detect_set = set(detect_list)
        exists_furniture_set = furniture_set.intersection(detect_set)
        furniture_num = len(exists_furniture_set)
        if furniture_num == 0:
            return False
        else:
            return True
    except Exception as e:
        return e

if __name__ == "__main__":
    print(detect_furniture_exists(FLAGS.img_path))