#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/11/5 下午5:17
# @Author  : houlinjie
# @Site    : 
# @File    : compute_class_label.py
# @Software: PyCharm


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from multiprocessing import Pool
from io import BytesIO
import logging
import os
import urllib
import request as req
import tensorflow as tf

config = tf.ConfigProto()
config.gpu_options.per_process_gpu_memory_fraction = 0.02

image_width = 256
image_height = 256
central_fraction = 0.875
# 访问图片前缀
domain = 'http://image.media.lianjia.com'
subprefix = '!m_fit,w_300,h_300'
AK = 'HT4ASES5HLDBPFKAOEDD'
SK = 'OMws9wMpOfknZm7JLi/zcb6aCEIGVejvneKl0hzp'
# expired time
EXP = 300

process_log = logging.getLogger('process log')
formatter = logging.Formatter('%(asctime)s-%(message)s')
process_handler.setFormatter(formatter)
process_log.setLevel(level=logging.IINFO)
process_log.addHandler(process_handler)

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

"""
request_url = get_sign(url, EXP)
response = req.get(request_url)

        if 200 != response.status_code:
            ret.append({"pic_url": img_url,
                        "state": 2})
            process_log.info('request_seq: %s|no result image url: %s', request_seq, img_url)
            return 0
        fd = BytesIO(response.content)
        image = Image.open(fd)
        # shrink_time = time.time()
        # scale_height = int(math.ceil((300 / float(image.size[0])) * image.size[1]))
        # pic = image.resize((300, scale_height), Image.BICUBIC)
        # shrink_elapsed_time = time.time() - shrink_time
        download_elapsed_time = time.time() - start_response
        process_log.info('request_seq: %s|image url: %s|download elapsed time: %s', request_seq, img_url,
                         download_elapsed_time)
    except Exception as e:
        exception_log.error('request_seq: %s|image url: %s|Error', request_seq, img_url, exc_info=True)
        ret.append({"pic_url": img_url,
                   "state": 1})
        return 0
"""

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