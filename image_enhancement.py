#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/5/7 5:42 PM
# @Author  : houlinjie
# @Site    : 
# @File    : image_enhancement.py
# @Software: PyCharm

import ctypes
import os
import logging
import urllib
import argparse
import time
from PIL import Image
# 访问图片前缀

class TestStruct(ctypes.Structure):
    _fields_ = [
        ("double_cast", ctypes.c_double),
        ("double_avg", ctypes.c_double)]

DOMAIN = 'http://image.media.lianjia.com'
parser = argparse.ArgumentParser()
parser.add_argument(
    '--src_file',
    required=True,
    type=str,
    help='save image url file'
)
parser.add_argument(
    '--path',
    required=True,
    type=str,
    help='save download image'
)
parser.add_argument(
    '--exception_log',
    required=True,
    type=str,
    help='record exception log'
)
parser.add_argument(
    '--process',
    required=True,
    type=str,
    help='record the process result'
)
parser.add_argument(
    '--problem',
    required=True,
    type=str,
    help='record the problem image information'
)

FLAGS, unparsed = parser.parse_known_args()
exception_log = logging.getLogger('exception log')
src_file = open(FLAGS.src_file)
exception_log.setLevel(level=logging.WARNING)
formatter = logging.Formatter('%(asctime)s-%(message)s')
exception_handler = logging.FileHandler(FLAGS.exception_log)
exception_handler.setFormatter(formatter)
exception_log.addHandler(exception_handler)
process_result = open(FLAGS.process, 'a+')
problem_result = open(FLAGS.problem, 'a+')

def download_image(img_url, path, filename):
    try:
        sock = urllib.urlopen(img_url)
        htmlcode = sock.read()
        sock.close()
        filedir = open(os.path.join(path, filename), "wb")
        filedir.write(htmlcode)
        filedir.close()
    except Exception as err:
        exception_log.error('open url image error: %s', err)

def main():
    test_struct = TestStruct()
    test_struct.double_cast = 0.0
    test_struct.double_avg = 0.0
    lib = ctypes.cdll.LoadLibrary("./libimage.so")
    lib.light.restype = TestStruct
    lib.clear2.restype = ctypes.c_double
    for line in src_file.readlines():
        try:
            url = line.strip('\n')
            filename = url.split('/')[-1]
            request_url = DOMAIN + url
            download_image(request_url, FLAGS.path, filename)
            img_path = FLAGS.path + "/" + filename
            img = Image.open(img_path)
            basename = os.path.basename(filename)
            pil_name = FLAGS.path + "/" + basename + '.jpg'
            img.save(pil_name)
            test_struct = lib.light(pil_name, request_url, test_struct)
            print(test_struct.double_cast)
            print(test_struct.double_avg)
            blur_cast = lib.clear2(pil_name, request_url)
            os.remove(img_path)
            os.remove(pil_name)
            process_result.write("request_url:{}\tfilename:{}\tlight_cast{}\tlight_avg{}\tblur_cast{}\n".format(
                                 request_url, filename, test_struct.double_cast, test_struct.double_avg, blur_cast))
            if test_struct.double_cast > 1:
                if test_struct.double_avg > 0:
                    problem_result.write("request_url:{}\tfilename:{}\tlight_cast{}\tlight_avg{}\tresult:{}\n".format(
                        request_url, filename, test_struct.double_cast, test_struct.double_avg, "light"))
                else:
                    problem_result.write("request_url:{}\tfilename:{}\tlight_cast{}\tlight_avg{}\tresult:{}\n".format(
                        request_url, filename, test_struct.double_cast, test_struct.double_avg, "dark"))
            if blur_cast < 10:
                problem_result.write("request_url:{}\tfilename:{}\tblur_cast{}\tresult:{}\n".format(request_url,
                                    filename, blur_cast, "blur"))
        except Exception as e:
            exception_log.error('Error', exc_info=True)
            os.remove(img_path)
            os.remove(pil_name)
            continue

if __name__ == "__main__":
    main()