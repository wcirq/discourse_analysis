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

        with open(filename_path, "rb") as infile:
            lines = infile.readlines()
            datas = [data.decode(encoding) for data in lines]
        datas = [data.strip("\n") for data in datas]
        datas = "".join(datas)
        datas = re.split('[,。.，！!?？；;]', datas)
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
    pattern = re.compile(u'―|\r|\t|\n|\.|-|:|;|\)|\(|\?|《|》|\[|\]|"|,|，| |。|？|；|#|“|”|％|…|．|【|】|：')  # 定义正则表达式匹配模式
    if isinstance(texts, list):
        texts = [re.sub(pattern, '', text) for text in texts]  # 将符合模式的字符去除
    else:
        texts = re.sub(pattern, '', texts)  # 将符合模式的字符去除
    return texts