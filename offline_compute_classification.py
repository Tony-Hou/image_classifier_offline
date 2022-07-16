#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/11/8 下午2:27
# @Author  : houlinjie
# @Site    : 
# @File    : offline_compute_all.py
# @Software: PyCharm

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from multiprocessing import Pool
from io import BytesIO, StringIO
from PIL import Image
import logging
import os
import urllib
import requests as req
import tensorflow as tf
import argparse
import time
import hashlib
import numpy as np
import sys
import imagehash


parser = argparse.ArgumentParser()
parser.add_argument(
    '--gpu',
    required=True,
    type=str,
    help='gpu num'
)
parser.add_argument(
    '--graph',
    required=True,
    type=str,
    help='Absolute path to graph file (.pb)'
)
parser.add_argument(
    '--process_log',
    required=True,
    type=str,
    help='record process log'
)
parser.add_argument(
    '--exception_log',
    required=True,
    type=str,
    help='record exception log'
)
parser.add_argument(
    '--result',
    required=True,
    type=str,
    help='save predict result file'
)
parser.add_argument(
    '--src_file',
    required=True,
    type=str,
    help='save url file'
)
image_width = 256
image_height = 256
num_channels = 3
global image_type
image_type = True
# expired time
EXP = 300
# 访问图片前缀
DOMAIN = 'http://image.media.lianjia.com'
AK = 'HT4ASES5HLDBPFKAOEDD'
SK = 'OMws9wMpOfknZm7JLi/zcb6aCEIGVejvneKl0hzp'
subprefix = '!m_fit,w_300,h_300'

config = tf.ConfigProto()
config.gpu_options.per_process_gpu_memory_fraction = 0.05

FLAGS, unparsed = parser.parse_known_args()
os.environ["CUDA_VISIBLE_DEVICES"] = FLAGS.gpucd 

process_log = logging.getLogger('process log')
exception_log = logging.getLogger('exception log')

process_log.setLevel(level=logging.INFO)
exception_log.setLevel(level=logging.WARNING)

formatter = logging.Formatter('%(asctime)s-%(message)s')

process_handler = logging.FileHandler(FLAGS.process_log)
exception_handler = logging.FileHandler(FLAGS.exception_log)

process_handler.setFormatter(formatter)
exception_handler.setFormatter(formatter)

process_log.addHandler(process_handler)
exception_log.addHandler(exception_handler)


# 签名算法
def get_sign(path, exp):
    ts = int(time.time())
    sign_dict = {}
    sign_dict['ak'] = AK
    sign_dict['ts'] = ts

    sign_dict['path'] = path
    sign_dict['exp'] = exp

    sign_list = []
    sign_list.append('ak')
    sign_list.append('path')
    sign_list.append('exp')
    sign_list.append('ts')
    sign_string = ""
    sorted_sign_list = sorted(sign_list)
    for key in sorted_sign_list:
        sign_string = sign_string + urllib.urlencode({key: sign_dict[key]}) + "&"
    sign_string = urllib.unquote(sign_string).decode('utf-8', 'replace').encode('gbk', 'replace')
    sign_string = sign_string + 'sk=' + SK
    md5_sign_string = hashlib.md5()
    md5_sign_string.update(sign_string)
    sign = md5_sign_string.hexdigest()
    sign_list.remove('path')
    request_url = ""
    for key in sign_list:
        request_url = request_url + urllib.urlencode({key: sign_dict[key]}) + "&"
    request_url = DOMAIN + path + "?" + request_url + "sign=" + sign
    return request_url


def load_graph(trained_model):
    """
    method 1: load graph as default graph.
    #Unpersists graph from file as default graph.
    with tf.gfile.GFile(trained_model, 'rb') as f:
         graph_def = tf.GraphDef()
         graph_def.ParseFromString(f.read())
         tf.import_graph_def(graph_def, name='')
    """
    #load graph
    with tf.gfile.GFile(trained_model, "rb") as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
        tf.import_graph_def(graph_def, name='')

    with tf.Graph().as_default() as graph:
        tf.import_graph_def(
            graph_def,
            input_map=None,
            return_elements=None,
            name=""
            )
    return graph


def main():
    global image_type

    def run_graph(image_string, sess):
        images1 = sess.run(image1, {image_str1: image_string})
        x_batch1 = images1.reshape(1, image_height, image_width, num_channels)
        feed_dict_tmp1 = {x1: x_batch1}
        result = sess.run(y_pred1, feed_dict=feed_dict_tmp1)
        return result

    g = load_graph(FLAGS.graph)
    session1 = tf.Session(graph=g, config=config)
    with g.as_default():
        # build graph
        image_str1 = tf.placeholder(tf.string)
        if image_type:
            image_raw_data1 = tf.image.decode_jpeg(image_str1, num_channels)
        else:
            image_raw_data1 = tf.image.decode_png(image_str1, num_channels)
        image1 = tf.image.convert_image_dtype(image_raw_data1, dtype=tf.uint8)
        if image_height and image_width:
            # Resize the image to the specified height and width
            image1 = tf.expand_dims(image1, 0)
            image1 = tf.image.resize_bilinear(image1, [image_height, image_width], align_corners=False)
            image1 = tf.squeeze(image1, [0])
        image1 = tf.subtract(image1, 0.5)
        image1 = tf.multiply(image1, 2.0)
        y_pred1 = session1.graph.get_tensor_by_name("y_pred:0")
        x1 = session1.graph.get_tensor_by_name("x:0")
    """
       目前对异常的图片(包括下载失败，无法正常读取，无结果图等情况)标识为"未知类型"
       202000000000   未知类型
       202000000100   卧室
       202000000201   客厅
       202000000300   厨房
       202000000400   卫生间
       'bathroom': 0, 'bedroom': 1, 'kitchen': 2, 'livingroom': 3, 'other': 4, 
    """
    predict_file = open(FLAGS.result, 'a+')
    src_file = open(FLAGS.src_file, 'r')
    for line in src_file.readlines():
        line = line.strip('\n').split()
        url = line[3]
        try:
            subfix = url.split('/')[-1].rsplit('.', 1)[1]
            if subfix == 'png':
                image_type = False
            else:
                image_type = True
        except Exception as e:
            image_type = True
        request_url = get_sign(url, EXP)
        try:
            response = req.get(request_url)
            # 无结果图的hash code值不存储
            if 200 != response.status_code:
                process_log.info('no result image: %s', url)
                line[5] = '202000000000'
                predict_file.write('{}\t{}\t{}\t{}\t{}\t{}\n'.format(line[0], line[1], line[2], line[3], line[4], line[5]))
                continue
            start_time = time.time()
            # 获取缩放后的图片
            class_img = response.content
            graph1_res = run_graph(class_img, session1)
            response.close()
        #    图片下载或无法正常读取时返回未知类型
        except Exception as e:
            exception_log.error('image url: %s|Error', url, exc_info=True)
            line[5] = '202000000000'
            predict_file.write('{}\t{}\t{}\t{}\t{}\t{}\n'.format(line[0], line[1], line[2], line[3], line[4], line[5]))
            continue
        try:
            label = np.argmax(graph1_res[0])
            if label == 0:
                elapsed_time = time.time() - start_time
                line[5] = '202000000400'
                process_log.info('image url: %s|download elapsed time: %s|bathroom probability: %f', url, elapsed_time,
                                                                                    graph1_res[0][0])
                predict_file.write('{}\t{}\t{}\t{}\t{}\t{}\n'.format(line[0], line[1], line[2], line[3], line[4], line[5]))
                continue
            elif label == 1:
                elapsed_time = time.time() - start_time
                line[5] = '202000000100'
                process_log.info('image url: %s|download elapsed time: %s|bedroom probability: %f', url, elapsed_time,
                                 graph1_res[0][1])
                predict_file.write('{}\t{}\t{}\t{}\t{}\t{}\n'.format(line[0], line[1], line[2], line[3], line[4], line[5]))
                continue
            elif label == 2:
                elapsed_time = time.time() - start_time
                line[5] = '202000000300'
                process_log.info('image url: %s|download elapsed time: %s|kitchen probability: %f', url,
                                                                    elapsed_time, graph1_res[0][2])
                predict_file.write('{}\t{}\t{}\t{}\t{}\t{}\n'.format(line[0], line[1], line[2], line[3], line[4],
                                                                     line[5]))
                continue
            elif label == 3:
                elapsed_time = time.time() - start_time
                line[5] = '202000000201'
                process_log.info('image url: %s|download elapsed time: %s|livingroom probability: %f', url, elapsed_time,
                                                                        graph1_res[0][3])
                predict_file.write('{}\t{}\t{}\t{}\t{}\t{}\n'.format(line[0], line[1], line[2], line[3], line[4], line[5]))
                continue
            elif label == 4:
                elapsed_time = time.time() - start_time
                line[5] = '202000000600'
                process_log.info('image url: %s|download elapsed time: %s|other probability: %f', url, elapsed_time,
                                              graph1_res[0][4])
                predict_file.write('{}\t{}\t{}\t{}\t{}\t{}\n'.format(line[0], line[1], line[2], line[3], line[4],
                                                                     line[5]))
                continue
        except Exception as e:
            exception_log.error('image url: %s|Error', url, exc_info=True)
            line[5] = '202000000000'
            predict_file.write('{}\t{}\t{}\t{}\t{}\t{}\n'.format(line[0], line[1], line[2], line[3], line[4], line[5]))
            pass
    predict_file.close()
    src_file.close()


if __name__ == "__main__":
    main()