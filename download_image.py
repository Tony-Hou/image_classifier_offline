#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/11/12 下午4:05
# @Author  : houlinjie
# @Site    : 
# @File    : download_image.py
# @Software: PyCharm

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
import os
import sys
import urllib
from PIL import Image
import time
import argparse
import logging
import hashlib

# expired time
EXP = 300
# 访问图片前缀
#DOMAIN = 'http://image.media.lianjia.com'
DOMAIN = 'http://storage.lianjia.com'
AK = 'HT4ASES5HLDBPFKAOEDD'
SK = 'OMws9wMpOfknZm7JLi/zcb6aCEIGVejvneKl0hzp'
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

FLAGS, unparsed = parser.parse_known_args()
abnormal_log = "abnormal.log"
logging.basicConfig(level=logging.INFO)
abnormal = open(abnormal_log, 'a+')
src_file = open(FLAGS.src_file)

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


def download_image(img_url, path, filename):
    try:
        sock = urllib.urlopen(img_url)
        htmlcode = sock.read()
        sock.close()
        filedir = open(os.path.join(path, filename), "wb")
        filedir.write(htmlcode)
        filedir.close()
    except Exception as err:
        logging.info('open url image error: %s', err)
        # abnormal_log.info('open url image error: %s', err)



def main():
    for line in src_file.readlines():
        line = line.strip('\n').split('\t')
        url = line[7]
        filename = url.split('/')[-1]
        request_url = DOMAIN + url
        print(url)
        # request_url = get_sign(url, EXP)
        rejectcodes = line[2]
        if rejectcodes == '230001001':                              #非3Dhome户型图
            download_image(request_url, './230001001', filename)
        if rejectcodes == '230001002':                              #标注简称
            download_image(request_url, './230001002', filename)
        if rejectcodes == '230001003':                               #功能间名称错误
            download_image(request_url, './230001003', filename)
        if rejectcodes == '230001004':                              #颜色错误
            download_image(request_url, './230001004', filename)
        if rejectcodes == '230001005':                              #方向标错误
            download_image(request_url, './230001005', filename)
        if rejectcodes == '230001006':                              #封闭空间
            download_image(request_url, './230001006', filename)
        if rejectcodes=='230001007':                                #显示不全
            download_image(request_url, './230001007', filename)
        if rejectcodes=='230001008':                                #户型图修饰
            download_image(request_url, './230001008', filename)
        if rejectcodes=='230001009':                                #未绘制楼梯
            download_image(request_url, './230001009', filename)
        if rejectcodes=='230001010':                                #字体大小不一致
            download_image(request_url, './230001010', filename)
        if rejectcodes=='230001011':                                #双重水印
            download_image(request_url, './230001011', filename)
        if rejectcodes=='230001012':                                #少绘制功能间
            download_image(request_url, './230001012', filename)
        if rejectcodes=='230001013':                                #入户门错误
            download_image(request_url, './230001013', filename)
        if rejectcodes=='230001014':                                #楼层错误
            download_image(request_url, './230001014', filename)
        if rejectcodes=='230001015':                                #虚线绘制错误
            download_image(request_url, './230001015', filename)
        if rejectcodes=='230001016':                                #门窗未按实际绘制
            download_image(request_url, './230001016', filename)
        if rejectcodes=='230001017':                                #格局绘制错误
            download_image(request_url, './230001017', filename)
        if rejectcodes=='230002001':                                #标准图与测绘图不符
            download_image(request_url, './230002001', filename)
        if rejectcodes=='230002002':                                #门或窗缺失
            download_image(request_url, './230002002', filename)
        if rejectcodes=='230003001':                                #门或窗缺失
            download_image(request_url, './230003001', filename)
        if rejectcodes=='230003002':                                #门窗位置错误
            download_image(request_url, './230003002', filename)
        if rejectcodes=='230003003':                                #功能间名称错误或缺失
            download_image(request_url, './230003003', filename)
        if rejectcodes=='230003004':                                #墙体尺寸，位置错误
            download_image(request_url, './230003004', filename)
        if rejectcodes=='230003005':                                #户型镜像
            download_image(request_url, './230003005', filename)
        if rejectcodes=='230003006':                                #多余门或窗
            download_image(request_url, './230003006', filename)
        if rejectcodes=='230003007':                                #缺失墙体
            download_image(request_url, './230003007', filename)
        if rejectcodes=='230003008':                                #未绘制楼梯
            download_image(request_url, './230003008', filename)
        if rejectcodes=='230003009':                                #楼梯位置错误
            download_image(request_url, './230003009', filename)
        if rejectcodes=='230003010':                                #楼层标注缺失或错误
            download_image(request_url, './230003010', filename)
        if rejectcodes=='230003011':                                #缺失功能间
            download_image(request_url, './230003011', filename)
        if rejectcodes=='230003012':                                #其它类问题
            download_image(request_url, './230003012', filename)
        if rejectcodes=='230002003':                                #门窗位置错误
            download_image(request_url, './230002003', filename)
        if rejectcodes=='230002004':                                #功能间名称错误或缺失
            download_image(request_url, './230002004', filename)
        if rejectcodes=='230002005':                                #墙体尺寸，位置错误
            download_image(request_url, './230002005', filename)
        if rejectcodes=='230002006':                                #户型镜像
            download_image(request_url, './230002006', filename)
        if rejectcodes=='230002007':                                #多余门或窗
            download_image(request_url, './230002007', filename)
        if rejectcodes=='230002008':                                #缺失墙体
            download_image(request_url, './230002008', filename)
        if rejectcodes=='230002009':                                #未绘制楼梯
            download_image(request_url, './230002009', filename)
        if rejectcodes=='230002010':                                #楼梯位置错误
            download_image(request_url, './230002010', filename)
        if rejectcodes=='230002011':                                #楼层标注缺失或错误
            download_image(request_url, './230002011', filename)
        if rejectcodes=='230002012':                                #缺失功能间
            download_image(request_url, './230002012', filename)
        if rejectcodes == '230002013':                              #其他类问题
            download_image(request_url, './230002013', filename)
        if rejectcodes=='230001018':                                #隐私空间标注错误
            download_image(request_url, './230001018', filename)
        if rejectcodes=='230001019':                                #门大小不一（90度）
            download_image(request_url, './230001019', filename)
        if rejectcodes=='230001020':                                #功能间数量与照片不符
            download_image(request_url, './230001020', filename)
        if rejectcodes=='230001021':                                #墙体不符
            download_image(request_url, './230001021', filename)
        if rejectcodes=='230001022':                                #其它类问题
            download_image(request_url, './230001022', filename)
        if rejectcodes=='220123':                                   #圈点图与参考图建立关系错误
            download_image(request_url, './220123', filename)
        if rejectcodes=='220124':                                   #开放厨房绘制错误
            download_image(request_url, './220124', filename)
        if rejectcodes=='220125':                                   #层高缺失
            download_image(request_url, './220125', filename)
        if rejectcodes=='220126':                                   #户型结构错误
            download_image(request_url, './220126', filename)
        if rejectcodes=='220127':                                   #户型描述缺失
            download_image(request_url, './220127', filename)
        if rejectcodes=='240001':                                   #画质问题
            download_image(request_url, './240001', filename)
        if rejectcodes=='240002':                                   #空间问题
            download_image(request_url, './240002', filename)
        if rejectcodes=='240003':                                   #隐私问题
            download_image(request_url, './240003', filename)
        if rejectcodes == '240004':                                 #数量、设置问题
            download_image(request_url, './240004', filename)
        if rejectcodes=='240005':                                   #人物问题
            download_image(request_url, './240005', filename)
        if rejectcodes=='240006':                                   #失真问题
            download_image(request_url, './240006', filename)
        if rejectcodes=='240007':                                   #水印
            download_image(request_url, './240007', filename)
        if rejectcodes=='240008':                                   #真实性
            download_image(request_url, './240008', filename)
        if rejectcodes=='240001001':                                #模糊
            download_image(request_url, './240001001', filename)
        if rejectcodes=='240001002':                                #黑暗
            download_image(request_url, './240001002', filename)
        if rejectcodes=='240001003':                                #曝光
            download_image(request_url, './240001003', filename)
        if rejectcodes=='240001004':                                #噪点
            download_image(request_url, './240001004', filename)
        if rejectcodes == '240002001':                                #无三面墙
            download_image(request_url, './240002001', filename)
        if rejectcodes == '240002002':                                #地面过大
            download_image(request_url, './240002002', filename)
        if rejectcodes == '240002003':                                #地面过小
            download_image(request_url, './240002003', filename)
        if rejectcodes == '240002004':                                #单一物品
            download_image(request_url, './240002004', filename)
        if rejectcodes == '240002005':                                #不能隔门隔墙拍摄
            download_image(request_url, './240002005', filename)
        if rejectcodes == '240003001':                              #隐私衣物
            download_image(request_url, './240003001', filename)
        if rejectcodes == '240003002':                                #马桶盖
            download_image(request_url, './240003002', filename)
        if rejectcodes == '240004001':                                #角度重复
            download_image(request_url, './240004001', filename)
        if rejectcodes == '240004002':                                #数量不符
            download_image(request_url, './240004002', filename)
        if rejectcodes == '240004003':                                #传错位置
            download_image(request_url, './240004003', filename)
        if rejectcodes == '240004004':
            download_image(request_url, './240004004', filename)
        if rejectcodes == '240005001':
            download_image(request_url, './240005001', filename)
        if rejectcodes == '240005002':
            download_image(request_url, './240005002', filename)
        if rejectcodes == '240005003':
            download_image(request_url, './240005003', filename)
        if rejectcodes == '240005004':
            download_image(request_url, './240005004', filename)
        if rejectcodes == '240006001':
            download_image(request_url, './240006001', filename)
        if rejectcodes == '240006002':
            download_image(request_url, './240006002', filename)
        if rejectcodes == '240007001':
            download_image(request_url, './240007001', filename)
        if rejectcodes == '240007002':
            download_image(request_url, './240007002', filename)
        if rejectcodes == '240008001':
            download_image(request_url, './240008001', filename)
        if rejectcodes == '240008002':
            download_image(request_url, './240008002', filename)
        if rejectcodes == '240009001':
            download_image(request_url, './240009001', filename)
        if rejectcodes == '240010001':
            download_image(request_url, './240010001', filename)
        if rejectcodes == '440001001':
            download_image(request_url, './440001001', filename)
        if rejectcodes == '440001009':
            download_image(request_url, './440001009', filename)
        if rejectcodes == '440001011':
            download_image(request_url, './440001011', filename)
        if rejectcodes == '440001013':
            download_image(request_url, './440001013', filename)
if __name__ == "__main__":
    main()