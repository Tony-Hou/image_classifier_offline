#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/11/29 下午6:38
# @Author  : houlinjie
# @Site    : 
# @File    : remove_duplicate_image.py
# @Software: PyCharm

from PIL import Image
import imagehash
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    '--dir',
    required=True,
    type=str,
    help='storage image dataset directory'
)

image_hashcode = []
FLAGS, unparsed = parser.parse_known_args()
for filename in os.listdir(FLAGS.dir):
     image_hash = imagehash.phash(Image.open(os.path.join(FLAGS.dir, filename)))
     print(image_hash)
     if image_hash in image_hashcode:
         os.remove(os.path.join(FLAGS.dir, filename))
     else:
         image_hashcode.append(image_hash)



