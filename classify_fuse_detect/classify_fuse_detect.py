#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/10/19 下午3:55
# @Author  : houlinjie
# @Site    : 
# @File    : classification_eval.py
# @Software: PyCharm

from collections import Counter
import urllib
import time
import tensorflow as tf
import os
import logging
import threading
import argparse
import sys
import shutil
import numpy as np
import base64
import requests


config = tf.ConfigProto()
config.gpu_options.per_process_gpu_memory_fraction = 0.1
DETECT_DOMAIN = "http://api.heimdallr.lianjia.com/v2/detect_furniture"
image_width = 256
image_height = 256
num_channels = 3
#central_fraction = 0.875
central_fraction = 0

# represent image type jpeg/png
global image_type
image_type = True
global livingroom_num
livingroom_num = 0
global bathroom_num
bathroom_num = 0
global kitchen_num
kitchen_num = 0
global bedroom_num
bedroom_num  = 0
global other_num
other_num = 0
"""
server_log = logging.handlers.TimedRotatingFileHandler('server.log', 'D')
server_log.setLevel(logging.DEBUG)
server_log.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s'))

error_log = logging.handlers.TimedRotatingFileHandler('error.log', 'D')
error_log.setLevel(logging.ERROR)
error_log.setFormatter(logging.Formatter(
    '%(asctime)s: %(message)s [in %(pathname)s:%(lineno)d]'))

app.logger.addHandler(server_log)
app.logger.addHandler(error_log)
"""


# 获取每个线程的返回值，对threading.Tthread进行封装
class MyThread(threading.Thread):
    def __init__(self, func, args=()):
        super(MyThread, self).__init__()
        self.func = func
        self.args = args

    def get_result(self):
        try:
            # 如果子线程不使用join function, 此处可能会报没有self.result 的错误
            return self.result
        except Exception:
            return None

    def run(self):
        self.result = self.func(*self.args)


parser = argparse.ArgumentParser()
parser.add_argument(
    '--graph1',
    required=True,
    type=str,
    help='Absolute path to graph file (.pb)'
)
parser.add_argument(
    '--path',
    required=True,
    type=str,
    help='path save image'
)
parser.add_argument(
    '--predict_result',
    required=True,
    type=str,
    help='save predict result filename'
)

"""
request data form  {'src_data': '', 'data_type': '1'}
src_data: 
         图片的url或者图片数据
data_type:
        1 代表图片的url
"""

"""
    Args: 
         None 
    Returns:
         data format: json string
         out={"image_name": value, "bathroom": value, "bedroom": value, "floorplan": value, "kitchen": value, 
              "livingroom": value, "other": value}
    return example:
                {
                  "bathroom": "0.099628", 
                  "bedroom": "0.434077", 
                  "floorplan": "0.00099361", 
                  "kitchen": "0.14794", 
                  "livingroom": "0.160443", 
                  "other": "0.156919"
                 }
"""
# UPLOAD_FOLDER = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + '/static')
UPLOAD_FOLDER = "/home/houlinjie001"
logging.basicConfig(level=logging.INFO)


def urllibopen(url, path, filename):
    try:
        sock = urllib.urlopen(url)
        htmlcode = sock.read()
        sock.close()
        filedir = open(os.path.join(path, filename), "wb")
        filedir.write(htmlcode)
        filedir.close()
    except Exception as err:
        logging.info('Url image open error: %s', err)


def object_detect(image_filename):
    try:
        time_stamp = str(int(time.time() * 100))
        request_id = time_stamp + image_filename
        img_base64 = base64.b64encode(open(image_filename, "rb").read())
        data = {'request_id': request_id, 'img_base64': img_base64}
        r = requests.post(DETECT_DOMAIN, data=data).json()
        return r
    except Exception as e:
        # print(e)
        # print(image_filename)
        pass

def load_graph(trained_model):
    """
    method 1: load graph as default graph.
    #Unpersists graph from file as default graph.
    with tf.gfile.GFile(trained_model, 'rb') as f:
         graph_def = tf.GraphDef()
         graph_def.ParseFromString(f.read())
         tf.import_graph_def(graph_def, name='')
    """
    # load graph
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


# image preprocess
def preprocess(img_name, height, width,
               central_fraction=0.875, scope=None):
    """
    :param image: preprocess image name
    :param height:
    :param width:
    :param central_fraction: fraction of the image to crop
    :param scope: scope  for name_scope
    :return: 3-D float Tensor of prepared image.
    """
    image_raw_data = tf.gfile.FastGFile(img_name, 'r').read()
    # file_extension = img_name.rsplit('.', 1)[1]
    # logging.info("file_extension: %s", file_extension)
    # if file_extension == 'jpg' or file_extension == 'jpeg':
    #     image_raw_data = tf.image.decode_jpeg(image_raw_data)
    # elif file_extension == 'png':
    #     image_raw_data = tf.image.decode_png(image_raw_data)
    #     image_raw_data = tf.image.encode_jpeg(image_raw_data)
    #     image_raw_data = tf.image.decode_jpeg(image_raw_data)
    image_raw_data = tf.image.decode_image(image_raw_data, num_channels)
    image = tf.image.convert_image_dtype(image_raw_data, dtype=tf.uint8)
    if central_fraction:
        image = tf.image.central_crop(image_raw_data, central_fraction=central_fraction)

    if height and width:
        # Resize the image to the specified  height and width
        image = tf.expand_dims(image, 0)
        image = tf.image.resize_bilinear(image, [height, width], align_corners=False)
        image = tf.squeeze(image, [0])
    image = tf.subtract(image, 0.5)
    image = tf.multiply(image, 2.0)
    return image


def main():
    def run_graph1(image_string, sess):
        images1 = sess.run(image1, {image_str1: image_string})
        x_batch1 = images1.reshape(1, image_height, image_width, num_channels)
        feed_dict_tmp1 = {x1: x_batch1}
        result = sess.run(y_pred1, feed_dict=feed_dict_tmp1)
        return result

    with tf.device('/device:GPU:1'):
        FLAGS, unparsed = parser.parse_known_args()
        g1 = load_graph(FLAGS.graph1)
        session1 = tf.Session(graph=g1, config=config)

        with g1.as_default():
            # build graph
            image_str1 = tf.placeholder(tf.string)
            if image_type:
                image_raw_data1 = tf.image.decode_jpeg(image_str1, num_channels)
            else:
                image_raw_data1 = tf.image.decode_png(image_str1, num_channels)
            image1 = tf.image.convert_image_dtype(image_raw_data1, dtype=tf.uint8)
            if central_fraction:
                image1 = tf.image.central_crop(image_raw_data1, central_fraction=central_fraction)
            if image_height and image_width:
                # Resize the image to the specified height and width
                image1 = tf.expand_dims(image1, 0)
                image1 = tf.image.resize_bilinear(image1, [image_height, image_width], align_corners=False)
                image1 = tf.squeeze(image1, [0])
            image1 = tf.subtract(image1, 0.5)
            image1 = tf.multiply(image1, 2.0)
            y_pred1 = session1.graph.get_tensor_by_name("y_pred:0")
            x1 = session1.graph.get_tensor_by_name("x:0")

    global counter
    counter = 0
    global image_num
    global bathroom_num
    global bedroom_num
    global kitchen_num
    global livingroom_num
    global other_num
    image_num = len(os.listdir(FLAGS.path))
    predict_file = open(FLAGS.predict_result, 'a+')
    for fd in os.listdir(FLAGS.path):
        try:
            detect_set = []
            start_time = time.time()
            image_path = os.path.join(FLAGS.path, fd)
            with open(image_path) as f:
                image_string = f.read()
                # 多线程
                threads = []
                thread1 = MyThread(run_graph1, args=(image_string, session1))
                thread2 = MyThread(object_detect, args=(image_path, ))
                threads.append(thread1)
                threads.append(thread2)
                for thread in threads:
                    thread.start()
                # run graph
                thread1.join()
                graph1_res = thread1.get_result()
                try:
                    thread2.join()
                    detect_result = thread2.get_result()
                    if detect_result['error_code'] == -1:
                        pass
                    else:
                        if len(detect_result['result']) == 0:
                            pass
                        else:
                            for i in range(len(detect_result['result'])):
                                detect_set.append(detect_result['result'][i]['label'])
                    predict_file.write('detect result: {} image filename: {}\n'.format(detect_set, image_path))
                except Exception as e:
                    predict_file.write('detect result: {} image filename: {}\n'.format(detect_set, image_path))
                    pass
                label = np.argmax(graph1_res[0])
                if label == 0:
                    bathroom_num = bathroom_num + 1
                    # shutil.move(image_path, 'predict_bathroom')
                    counter = counter + 1
                    elapsed_time = time.time() - start_time
                    predict_file.write('image_path: {},ground truth num: {},probablity: {}\n'.format(image_path, 0,
                                                                                                     graph1_res[0]))
                    sys.stdout.write(
                        '\r>> -_- Classify image -_-  %d/%d  elapsed_time %f' % (counter, image_num, elapsed_time))
                    sys.stdout.flush()
                    continue
                elif label == 1:
                    if 'toilet' in detect_set:
                        bathroom_num = bathroom_num + 1
                        # shutil.move(image_path, 'predict_bathroom')
                        predict_file.write(
                            'image_path: {}, ground truth num: {}, probablity: {}\n'.format(image_path, 0,
                                                                                            graph1_res[0]))
                    else:
                        bedroom_num = bedroom_num + 1
                        # shutil.move(image_path, 'predict_bedroom')
                        predict_file.write(
                            'image_path: {}, ground truth num: {}, probablity: {}\n'.format(image_path, 1,
                                                                                            graph1_res[0]))
                    counter = counter + 1
                    elapsed_time = time.time() - start_time
                    sys.stdout.write(
                        '\r>> -_- Classify image -_-  %d/%d  elapsed_time %f' % (counter, image_num, elapsed_time))
                    sys.stdout.flush()
                    continue
                elif label == 2:
                    if 'toilet' in detect_set:
                        bathroom_num = bathroom_num + 1
                        # shutil.move(image_path, 'predict_bathroom')
                        predict_file.write(
                            'image_path: {}, ground truth num: {}, probablity: {}\n'.format(image_path, 0,
                                                                                            graph1_res[0]))
                    else:
                        kitchen_num = kitchen_num + 1
                        # shutil.move(image_path, 'predict_kitchen')
                        predict_file.write(
                            'image_path: {}, ground truth num: {}, probablity: {}\n'.format(image_path, 2,
                                                                                            graph1_res[0]))
                    counter = counter + 1
                    elapsed_time = time.time() - start_time
                    sys.stdout.write(
                        '\r>> -_- Classify image -_-  %d/%d  elapsed_time %f' % (counter, image_num, elapsed_time))
                    sys.stdout.flush()
                    continue
                elif label == 3:
                    if 'bed' in detect_set and graph1_res[0][1] > 0.3:
                        bedroom_num = bedroom_num + 1
                        # shutil.move(image_path, './predict_bedroom')
                        predict_file.write(
                            'image_path: {},ground truth num:{}, probablity: {}\n'.format(image_path, 1,
                                                                                          graph1_res[0]))
                    else:
                        livingroom_num = livingroom_num + 1
                        # shutil.move(image_path, './predict_livingroom')
                        predict_file.write(
                            'image_path: {},ground truth num:{}, probablity: {}\n'.format(image_path, 3,
                                                                                          graph1_res[0]))
                    counter = counter + 1
                    elapsed_time = time.time() - start_time
                    sys.stdout.write(
                        '\r>> -_- Classify image -_-  %d/%d  elapsed_time %f' % (counter, image_num, elapsed_time))
                    sys.stdout.flush()
                    continue
                elif label == 4:
                    other_num = other_num + 1
                    # shutil.move(image_path, 'predict_other')
                    counter = counter + 1
                    elapsed_time = time.time() - start_time
                    predict_file.write(
                        'image_path: {},ground truth num:{}, probablity: {}\n'.format(image_path, 4, graph1_res[0]))
                    sys.stdout.write(
                        '\r>> -_- Classify image -_-  %d/%d  elapsed_time %f' % (counter, image_num, elapsed_time))
                    sys.stdout.flush()
                    continue
        except Exception as e:
            print(e)
            pass

    print('bathroom_num %d bedroom_num %d kitchen_num %d livingroom_num %d other_num %d', bathroom_num, bedroom_num,
          kitchen_num, livingroom_num, other_num)
if __name__ == "__main__":
    main()
