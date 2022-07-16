#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/31 下午2:19
# @Author  : houlinjie
# @Site    : 
# @File    : download_generate_hash_interface.py
# @Software: PyCharm

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from PIL import Image
from io import BytesIO
from flask import Flask, request, jsonify, Response
from multiprocessing.dummy import Pool as ThreadPool
import logging.handlers
import os
import sys
import logging
import imagehash
import time
import json
import urllib
import requests as req
import threading
import datetime
import shutil
import glob
import hashlib

# 访问图片前缀
DOMAIN = 'http://image.media.lianjia.com'
subprefix = '!m_fit,w_300,h_300'
AK = 'HT4ASES5HLDBPFKAOEDD'
SK = 'OMws9wMpOfknZm7JLi/zcb6aCEIGVejvneKl0hzp'
EXP = 300
# request id
global request_id
request_id = int(time.time() * 1000000)
q = threading.Lock()
# APP_LOG_DIR = os.environ['MATRIX_APPLOGS_DIR'] + "/"
APP_LOG_DIR = "./"
process_log_filename = APP_LOG_DIR + "process" + str(request_id) + ".log"
exception_log_filename = APP_LOG_DIR + "exception" + str(request_id) + ".log"
process_log = logging.getLogger('process log')
exception_log = logging.getLogger('exception log')
formatter = logging.Formatter('%(asctime)s -%(message)s')
process_handler = logging.handlers.TimedRotatingFileHandler(process_log_filename, when='midnight')
exception_handler = logging.handlers.TimedRotatingFileHandler(exception_log_filename, when='midnight')
process_log.suffix = "%Y-%m-%d"
exception_log.suffix = "%Y-%m-%d"

process_handler.setFormatter(formatter)
exception_handler.setFormatter(formatter)

process_log.setLevel(level=logging.INFO)
exception_log.setLevel(level=logging.WARNING)

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


# 解析请求中的数据把数据存放到队列中
# Args:
#     req_data: 请求数据
# Returns:
#        None
def download_and_generate_hash(img_url, result, ret, request_seq):
    try:
        # 判断img_url 是否为空
        start_response_time = time.time()
        process_log.info("img_url: %s|start response time: %s", img_url, time.time())
        result.add(img_url)
        if img_url == "":
            ret.append({"pic_url": "", "state": 1})
            process_log.info('request_seq: %s|image url is: %s', request_seq, '')
            return 0
        url = img_url + subprefix
        start_response = time.time()
        req_url = get_sign(url, EXP)
        s = req.session()
        s.keep_alive = False
        response = s.get(req_url)
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
    try:
        gen_hash_start = time.time()
        hash_code = imagehash.phash(image)
        gen_hash_elapsed_time = time.time() - gen_hash_start
        fd.close()
        image.close()
        # 记录开始生成hash的时间以及所消耗时间
        total_elapsed_time = time.time() - start_response_time
        process_log.info('request_seq: %s|image url: %s|generate hash elapsed time: %s|total_elapsed: %s|hash_code: %s',
                         request_seq, img_url, gen_hash_elapsed_time, total_elapsed_time, hash_code)
        ret.append({"pic_url": img_url,
                    "state": 0,
                    "hash_code": str(hash_code)})
    except Exception as e:
        # 保存异常值到log日志
        exception_log.error('request_seq: %s|image url: %s|Error', request_seq, img_url, exc_info=True)
        ret.append({"pic_url": img_url,
                    "state": 1})
        return 0


def parse_data_task(data, request_num):
    # 保存url的列表
    url_list = set([])
    # result_list
    result_list = set([])
    ret_value = []
    download_pool = ThreadPool(16)
    try:
        j_data = json.loads(data)
    except Exception as e:
        exception_log.error('request_num: %s|Error', request_num, exc_info=True)
        ret_val = {
                     "errorCode": 1,
                     "errorMsg": "invalid json string"
                  }
        return jsonify(ret_val)
    # 解析json string 过程中发生错误
    try:
        for x in j_data['params']:
            picture_url = x['pic_url']
            url_list.add(picture_url)
    except Exception as e:
        exception_log.error('request_num: %s|Error', request_num, exc_info=True)
        ret_val = {
                    "errorCode": 1,
                    "errorMsg": "parameter error"
                   }
        return jsonify(ret_val)
    try:
        for img_url in url_list:
            lst_var = [img_url, result_list, ret_value, request_num]
            download_pool.apply_async(download_and_generate_hash, lst_var)
        download_pool.close()
        download_pool.join()
    except Exception as e:
        exception_log.error('request_num: %s|Error', request_num, exc_info=True)
        ret_val = {
            "errorCode": 1,
            "errorMsg": "parameter error"
        }
        return jsonify(ret_val)
    if url_list.issubset(result_list):
        out = {"errorCode": 0,
               "errorMsg": "success",
               "data": ret_value}
        return json.dumps(out)


app = Flask(__name__)


@app.route('/single-image-process/', methods=['POST', 'GET'])
def single_image_process():
    global request_id
    q.acquire()
    request_id = request_id + 1
    q.release()
    start_parse_request_time = time.time()
    try:
        data = request.get_data()
    except Exception as e:
        exception_log.error('request_id: %s|Error', request_id, exc_info=True)
        ret_value = {
                       "errorCode": 1,
                       "errorMsg": "parameter error"
                    }
        return jsonify(ret_value)
    try:
        j_data = json.loads(data)
    except Exception as e:
        exception_log.error('request_id: %s|Error', request_id, exc_info=True)
        ret_value = {
                       "errorCode": 1,
                       "errorMsg": "cannot parse json string"
                    }
        return jsonify(ret_value)
    try:
        # 如果img_url 的值为NULL,返回错误
        img_url = j_data['pic_url']
        if img_url == "":
            ret_value = {
                "errorCode": 1,
                "errorMsg": "parameter error"
            }
            return jsonify(ret_value)
    except Exception as e:
        exception_log.error('request_id: %s|Error', request_id, exc_info=True)
        ret_value = {
                       "errorCode": 1,
                       "errorMsg": "parameter error"
                    }
        return jsonify(ret_value)
    download_url = img_url + subprefix
    req_url = get_sign(download_url, EXP)
    try:
        start_response = time.time()
        s = req.session()
        s.keep_alive = False
        response = s.get(req_url)
        if 200 != response.status_code:
            ret_value = {
                           "errorCode": 2,
                           "errorMsg": "no result picture",
                           "pic_url": img_url
                        }
            return jsonify(ret_value)
        fd = BytesIO(response.content)
        image = Image.open(fd)
        download_time = time.time() - start_response
        # 记录图片开始下载时间以及所消耗时间
        process_log.info('request_id: %s|image url: %s|download elapsed time: %s|Error', request_id, url, download_time,
                         exc_info=True)
    except Exception as e:
        exception_log.error('request_id: %s|image url: %s|Error', request_id, url, exc_info=True)
        ret_value = {
                       "errorCode": 1,
                       "errorMsg": "download image error"
                     }
        return jsonify(ret_value)
    try:
        gen_hash_start = time.time()
        hash_value = imagehash.phash(image)
        ret_value = {
                       "errorCode": 0,
                       "errorMsg": "success",
                       "pic_url": img_url,
                       "hash_code": str(hash_value)
                     }
        gen_hash_elapsed_time = time.time() - gen_hash_start
        elapsed_time = time.time() - start_parse_request_time
        # 记录开始生成hash的时间以及所消耗时间
        process_log.info('REQUEST_ID: %s|client IP: %s|request method: %s|request URL: %s|request parameter: %s|'
                         'HTTP_CODE: %d|response time: %s|hash_value: %s|image url: %s|generate hash elapsed time: %s|',
                         request_id, request.remote_addr, request.method, request.path,j_data, ret_value['errorCode'],
                         elapsed_time, hash_value, img_url, gen_hash_elapsed_time)
        fd.close()
        image.close()
    except Exception as e:
        exception_log.error('request_id: %s|image url: %s|Error', request_id, url, exc_info=True)
        ret_value = {
                       "errorCode": 1,
                       "errorMsg": "generate hash value error"
                     }
        return jsonify(ret_value)
    finally:
        process_log.info('REQUEST_ID:%s|client IP:%s|request method:%s|request URL:%s|request parameter:%s|HTTP_CODE%d|'
                         'response time:%s', request_id,request.remote_addr, request.method, request.path, data, 1,
                         elapsed_time)
    return jsonify(ret_value)


@app.route('/batch-image-process/', methods=['POST', 'GET'])
def batch_image_process():
    global request_id
    q.acquire()
    request_id = request_id + 1
    q.release()
    try:
        start_time = time.time()
        data = request.get_data()
    except Exception as e:
        exception_log.error('request_id: %s|Error', request_id, exc_info=True)
        ret_val = {
                     "errorCode": 1,
                     "errorMsg": "get request data error"
                  }
        return jsonify(ret_val)
    finally:
        process_log.info('REQUEST_ID:%s|client IP:%s|request method:%s|request URL:%s|request parameter:%s|HTTP_CODE:%d'
                         '|response time:%s', request_id, request.remote_addr, request.method, request.path, data, 1,
                         (time.time() - start_time))
    hash_code_result = parse_data_task(data, request_id)
    elapsed_time = time.time() - start_time
    process_log.info('REQUEST_ID:%s|client IP:%s|request method:%s|request URL:%s|request parameter:%s|HTTP_CODE:%d|'
                     'response time:%s|req_size:%d', request_id, request.remote_addr, request.method, request.path, data,
                     json.loads(hash_code_result)['errorCode'], elapsed_time, len(hash_code_result))
    return hash_code_result


