#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/11/29 下午12:40
# @Author  : houlinjie
# @Site    : 
# @File    : classify_fuse_detect_model_test.py
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
import base64

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
# expired time
EXP = 300
# 访问图片前缀
DOMAIN = 'http://image.media.lianjia.com'
AK = 'HT4ASES5HLDBPFKAOEDD'
SK = 'OMws9wMpOfknZm7JLi/zcb6aCEIGVejvneKl0hzp'
suffix = '!m_fit,w_300,h_300'
DETECT_DOMAIN = "http://api.heimdallr.lianjia.com/v2/detect_furniture"
global detect_set
detect_set = []
config = tf.ConfigProto()
config.gpu_options.per_process_gpu_memory_fraction = 0.05
FLAGS, unparsed = parser.parse_known_args()
os.environ["CUDA_VISIBLE_DEVICES"] = FLAGS.gpu
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

class MyThread(threading.Thread):
    def __init__(self, func, args=()):
        super(MyThread, self).__init__()
        self.func = func
        self.args = args

    def get_result(self):
        try:
        #如果子线程不使用join function, 此处可能会报没有self.result 的错误
            return self.result
        except Exception:
            return None

    def run(self):
        self.result = self.func(*self.args)

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


def object_detect(image_url):
    try:
        filename = image_url.split('/')[-1]
        time_stamp = str(int(time.time() * 100))
        request_id = time_stamp + ',' + filename
        url = domain + image_url + suffix
        s = requests.session()
        s.keep_alive = False
        response = s.get(url)
        img_base64 = base64.b64encode(response.content)
        data = {'request_id': request_id, 'img_base64': img_base64}
        r = requests.post(DETECT_DOMAIN, data=data).json()
        return r
    except Exception as e:
        exception_log.error('object detect image url: %s|Error', image_url, exc_info=True)


def main():
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
        image_raw_data1 = tf.image.decode_image(image_str1, num_channels)
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
        request_url = get_sign(url, EXP)
        try:
            response = req.get(request_url)
            # 无结果图的hash code值不存储
            if 200 != response.status_code:
                process_log.info('no result image: %s', url)
                line[5] = '202000000000'
                predict_file.write('{}\t{}\t{}\t{}\t{}\t{}\n'.format(line[0], line[1], line[2], line[3], line[4], line[5]))
                continue
            start_download_time = time.time()
            class_img = response.content
            download_elapsed_time = time.time() - start_download_time
            start_time = time.time()
            threads_set = []
            thread_classify = MyThread(run_graph, args=(class_img, session1))
            thread_detect = MyThread(object_detect, args=(url, ))
            threads_set.append(thread_classify)
            threads_set.append(thread_detect)
            for thread in threads:
                thread.start()
            thread_classify.join()
            graph1_res = thread_classify.get_result()
            thread_detect.join()
            detect_result = thread_detect.get_result()
            if detect_result['error_code'] == -1:
                pass
            else:
                if len(r['result']) == 0:
                    pass
                else:
                    for i in range(len(r['result'])):
                        global detect_set
                        detect_set.append(r['result'][i]['label'])
            response.close()
        #    图片下载或无法正常读取时返回未知类型
        except Exception as e:
            exception_log.error('image url: %s|Error', url, exc_info=True)
            line[5] = '202000000000'
            predict_file.write('{}\t{}\t{}\t{}\t{}\t{}\n'.format(line[0], line[1], line[2], line[3], line[4], line[5]))
            continue
        try:
            label = np.argmax(graph1_res[0])
            # bathroom
            if label == 0:
                elapsed_time = time.time() - start_time
                line[5] = '202000000400'
                process_log.info('image url: %s|download elapsed time: %s|classify compute time: %s|bathroom '
                                 'probability:%f', url, download_elapsed_time, elapsed_time, graph1_res[0][0])
                predict_file.write('{}\t{}\t{}\t{}\t{}\t{}\n'.format(line[0], line[1], line[2], line[3], line[4], line[5]))
                continue
            elif label == 1:
                # bedroom
                elapsed_time = time.time() - start_time
                global detect_set
                if 'toilet' in detect_set:
                    line[5] = '202000000400'
                else:
                    line[5] = '202000000100'
                process_log.info('image url: %s|download elapsed time: %s|classify compute time: %s|bedroom '
                                 'probability: %f', url, download_elapsed_time, elapsed_time, graph1_res[0][1])
                predict_file.write('{}\t{}\t{}\t{}\t{}\t{}\n'.format(line[0], line[1], line[2], line[3], line[4], line[5]))
                continue
            elif label == 2:
                # kitchen
                elapsed_time = time.time() - start_time
                global detect_set
                if 'toilet' in detect_set:
                    line[5] = '202000000400'
                else:
                    line[5] = '202000000300'
                process_log.info('image url: %s|download elapsed time: %s|classify compute time: %s|kitchen '
                                 'probability: %f', url, download_elapsed_time, elapsed_time, graph1_res[0][2])
                predict_file.write('{}\t{}\t{}\t{}\t{}\t{}\n'.format(line[0], line[1], line[2], line[3], line[4],
                                                                     line[5]))
                continue
            elif label == 3:
                # livingroom
                elapsed_time = time.time() - start_time
                #
                global detect_set
                if 'bed' in detect_set or 'wardrobe' in detect_set:
                    line[5] = '202000000100'
                else:
                    line[5] = '202000000201'
                process_log.info('image url: %s|download elapsed time: %s|classify compute time: %s|livingroom '
                                 'probability: %f', url, download_elapsed_time, elapsed_time, graph1_res[0][3])
                predict_file.write('{}\t{}\t{}\t{}\t{}\t{}\n'.format(line[0], line[1], line[2], line[3], line[4], line[5]))
                continue
            elif label == 4:
                # outdoor
                elapsed_time = time.time() - start_time
                line[5] = '202000000600'
                process_log.info('image url: %s|download elapsed time: %s|classify compute time: %s|other '
                                 'probability: %f', url, download_elapsed_time, elapsed_time, graph1_res[0][4])
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