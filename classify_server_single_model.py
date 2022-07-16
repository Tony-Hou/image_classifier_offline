#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 26 14:39:19 2017 

@author: houlinjie
"""

from tornado.wsgi import WSGIContainer 
from tornado.httpserver import HTTPServer 
from tornado.ioloop import IOLoop
from flask import Flask, request, jsonify
import json
import urllib
import time
import tensorflow as tf
import os
import logging
from werkzeug import secure_filename
import threading
import argparse
import sys



config = tf.ConfigProto()
config.gpu_options.per_process_gpu_memory_fraction = 0.1

image_width = 256
image_height = 256
num_channels = 3
central_fraction = 0.875

#represent image type jpeg/png
global image_type
image_type = True
UPLOAD_FOLDER = "/home/houlinjie001"

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
        #如果子线程不使用join function, 此处可能会报没有self.result 的错误
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
# parser.add_argument(
#     '--graph2',
#     required=True,
#     type=str,
#     help='Absolute path to graph file (.pb)'
# )

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
UPLOAD_FOLDER = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + '/static')
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
    



def run_graph1(image_string, sess):
    images1 = sess.run(image1, {image_str1: image_string})
    x_batch1 = images1.reshape(1, image_height, image_width, num_channels)
    feed_dict_tmp1 = {x1: x_batch1}
    result = sess.run(y_pred1, feed_dict=feed_dict_tmp1)
    return result

# def run_graph2(image_string, sess):
#     images2 = sess.run(image2, {image_str2: image_string})
#     x_batch2 = images2.reshape(1, image_height, image_width, num_channels)
#     feed_dict_tmp2 = {x2: x_batch2}
#     result = sess.run(y_pred2, feed_dict=feed_dict_tmp2)
#     return result


def merge_result(fd, sess1):
    with open(os.path.join(UPLOAD_FOLDER, fd)) as f:
        image_string = f.read()

        threads = []
        thread1 = MyThread(run_graph1, args=(image_string, sess1))
        threads.append(thread1)
        for thread in threads:
            thread.start()
        
        # run graph
        thread1.join()
        graph1_res = thread1.get_result()

        # images1 = sess1.run(image1, {image_str1: image_string})
        # x_batch1 = images1.reshape(1, image_height, image_width, num_channels)
        # feed_dict_tmp1 = {x1: x_batch1}
        # graph1_res = sess1.run(y_pred1, feed_dict=feed_dict_tmp1)
        #
        #
        # images2 = sess2.run(image2, {image_str2: image_string})
        # x_batch2 = images2.reshape(1, image_height, image_width, num_channels)
        # feed_dict_tmp2 = {x2: x_batch2}
        # graph2_res = sess2.run(y_pred2, feed_dict=feed_dict_tmp2)

        # 判断户型图
        # if graph1_res[0][0] > 0.6:
        #     out = {"floorplan": str(graph1_res[0][0])}
        #     logging.info("graph1_res[0][0]: %f:", graph1_res[0][0])
        #     return jsonify(out)
        # # 判断卫生间 最原始的阈值是0.6, 降低到 0.55
        # elif graph1_res[0][1] > 0.6 and graph2_res[0][0] > 0.55:
        #     out = {"bathroom": str(graph2_res[0][0])}
        #     logging.info("graph2_res[0][0]: %f:", graph2_res[0][0])
        #     return jsonify(out)
        # # 判断卧室
        # elif graph1_res[0][1] > 0.6 and graph2_res[0][1] > 0.6:
        #     out = {"bedroom": str(graph2_res[0][1])}
        #     logging.info("graph2_res[0][1]: %f:", graph2_res[0][1])
        #     return jsonify(out)
        # # 判断厨房
        # elif graph1_res[0][1] > 0.6 and graph2_res[0][2] > 0.6:
        #     out = {"kitchen": str(graph2_res[0][2])}
        #     logging.info("graph2_res[0][2]: %f:", graph2_res[0][2])
        #     return jsonify(out)
        # # 判断客厅
        # elif graph1_res[0][1] > 0.6 and graph2_res[0][3] > 0.6:
        #     out = {"livingroom": str(graph2_res[0][3])}
        #     logging.info("graph2_res[0][3]: %f:", graph2_res[0][3])
        #     return jsonify(out)
        # # other
        # elif graph1_res[0][1] > 0.6 and graph2_res[0][4] > 0.5:
        #     out = {"other": str(graph2_res[0][4])}
        #     logging.info("graph2_res[0][4]: %f:", graph2_res[0][4])
        #     return jsonify(out)
        # # 归为非房产类图片，过滤规则设置的比较宽松，如果还不符合就不应该上传
        # else:
        #     out = {"illegal picture!": str(0)}
        #     logging.info("illlegal picture!!!")
        #     return jsonify(out)
        out = {"bathroom": str(graph1_res[0][0]),
               "bedroom": str(graph1_res[0][1]),
               "kitchen": str(graph1_res[0][2]),
               "livingroom": str(graph1_res[0][3]),
               "other": str(graph1_res[0][4])}
        return jsonify(out)

app = Flask(__name__)
FLAGS, unparsed = parser.parse_known_args()
g1 = load_graph(FLAGS.graph1)
# g2 = load_graph(FLAGS.graph2)
session1 = tf.Session(graph=g1, config=config)
# session2 = tf.Session(graph=g2, config=config)
with g1.as_default():
    #build graph
    image_str1 = tf.placeholder(tf.string)
    if image_type:
        image_raw_data1 = tf.image.decode_jpeg(image_str1, num_channels)
    else:
        image_raw_data1 = tf.image.decode_png(image_str1, num_channels)
    image1 = tf.image.convert_image_dtype(image_raw_data1, dtype=tf.uint8)
    # if central_fraction:
    #     image1 = tf.image.central_crop(image_raw_data1, central_fraction=central_fraction)
    if image_height and image_width:
        #Resize the image to the specified height and width
        image1 = tf.expand_dims(image1, 0)
        image1 = tf.image.resize_bilinear(image1, [image_height, image_width], align_corners=False)
        image1 = tf.squeeze(image1, [0])
    image1 = tf.subtract(image1, 0.5)
    image1 = tf.multiply(image1, 2.0)
    y_pred1 = session1.graph.get_tensor_by_name("y_pred:0")
    x1 = session1.graph.get_tensor_by_name("x:0")
# with g2.as_default():
#     #build graph
#     image_str2 = tf.placeholder(tf.string)
#     if image_type:
#         image_raw_data2 = tf.image.decode_jpeg(image_str2, num_channels)
#     else:
#         image_raw_data2 = tf.image.decode_png(image_str2, num_channels)
#     image2 = tf.image.convert_image_dtype(image_raw_data2, dtype=tf.uint8)
#     if central_fraction:
#         image2 = tf.image.central_crop(image_raw_data2, central_fraction=central_fraction)
#     if image_height and image_width:
#         #Resize the image to the specified height and width
#         image2 = tf.expand_dims(image2, 0)
#         image2 = tf.image.resize_bilinear(image2, [image_height, image_width], align_corners=False)
#         image2 = tf.squeeze(image2, [0])
#     image2 = tf.subtract(image2, 0.5)
#     image2 = tf.multiply(image2, 2.0)
#     y_pred2 = session2.graph.get_tensor_by_name("y_pred:0")
#     x2 = session2.graph.get_tensor_by_name("x:0")

@app.route('/', methods=['POST'])
def parse_request():
    try:
        if request.form['data_type'] == u'1':
            start_request = time.time()
            url = request.form['src_data']
            #parse url return image data
            #传给预处理，经过模型计算返回 分类结果
            #
            fd = url.rsplit('/', 1)[1] + '.1000.jpg'
            start_download = time.time()
            urllibopen(url, UPLOAD_FOLDER, fd)
            download_time_elapsed = time.time() - start_download
            start_classify = time.time()
            ret_value = merge_result(fd, session1)
            #ret_value = run_graph(fd, sess)
            classify_time_elapsed = time.time() - start_classify
            total_elapsed_time = time.time() - start_request
            logging.info("download_time_elapsed: %f", download_time_elapsed)
            logging.info("classify_time_elapsed: %f", classify_time_elapsed)
            logging.info("total_elapsed_time: %f", total_elapsed_time)
            filename = os.path.join(UPLOAD_FOLDER, fd)
            os.remove(filename)
            return ret_value
        elif request.form['data_type'] == u'2':
            #recieve picture data
            #传给预处理，经过模型计算返回分类结果
            start_download = time.time()
            upload_file = request.files['src_data']
            filename = secure_filename(upload_file.filename)
            upload_file.save(os.path.join(UPLOAD_FOLDER, filename))
            subfix = filename.rsplit('.', 1)[1]
            if subfix == 'jpg':
                image_type = True
            elif subfix == 'png':
                image_type = False
            download_time_elapsed = time.time() - start_download
            start_classify = time.time()
            ret_value = merge_result(filename, session1)
            logging.info("download_time_elapsed: %f", download_time_elapsed)
            #ret_value = run_graph(filename, sess)
            classify_time_elapsed = time.time() - start_classify
            logging.info("classify_time_elapsed: %f", classify_time_elapsed)
            total_elapsed_time = time.time() - start_download
            logging.info("total_elapsed_time: %f", total_elapsed_time)
            return ret_value

    except Exception as e:
        print e
        return repr(e)
app.run(host="10.200.0.163", port=int("16888"), debug=True, use_reloader=False)

#if __name__ == '__main__':
# linux
"""
http_server = HTTPServer(WSGIContainer(app)) 
http_server.bind(16888, '10.200.0.174') 
http_server.start(num_processes=6) 
IOLoop.instance().start()        
"""
