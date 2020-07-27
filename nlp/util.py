# -*- coding: utf-8 -*- 
# @Time 2020/6/1 12:57
# @Author wcy
import os
import re

import chardet
import numpy as np

from common.logger_config import logger


def read_txt(filename_path):
    try:
        bytes = min(2048, os.path.getsize(filename_path))
        raw = open(filename_path, 'rb').read(bytes)
        result = chardet.detect(raw)
        encoding = result['encoding']
        encoding = "gbk" if encoding=='GB2312' else encoding
        with open(filename_path, "rb") as infile:
            lines = infile.readlines()
            datas = [data.decode(encoding) for data in lines]
        # datas = [data.strip("\n") for data in datas]
        # datas = "".join(datas)
        # datas = re.split('[。.！!?？；;]', datas)
        datas = "".join(datas)
        datas = re.sub("[\n|\r]", "", datas)
        # 按符号切分文章
        datas = re.split('[。.，,！!?？；;]', datas)
        # 去掉空字符串和去掉首尾空格
        datas = [data.strip() for data in datas if data != ""]
    except Exception as e:
        logger.error(filename_path)
        return [""]

    return datas


def log_likelihood(l1, l2):
    """计算对数似然率"""
    if l2 == 0:
        l2 = 1e-9
    result = np.log(l1 / l2)
    return result


def pretreatment_texts(texts):
    pattern = re.compile(
        u'―|\r|\t|\n|-|:|\)|\(|《|》|\[|\]|"|#|“|”|％|…|【|】|：|«|»|—')  # 定义正则表达式匹配模式，不能去掉空格
    if isinstance(texts, list):
        texts = [re.sub(pattern, '', text) for text in texts]  # 将符合模式的字符去除
    else:
        texts = re.sub(pattern, '', texts)  # 将符合模式的字符去除
    return texts


def get_chinese_ratio(text, num=300):
    """
    判断字符串中，中文的占比
    :param num:
    :param char: 字符串
    :return:总的
    """
    if isinstance(text, list):
        text = " ".join(text)
    text = text[:num]
    count = 0
    total = len(re.sub(" ", "", text))
    if total == 0:
        return 0
    for item in text:
        if 0x4E00 <= ord(item) <= 0x9FA5:
            count += 1
    return count / total


if __name__ == '__main__':
    read_txt("./2019_3a0.txt")