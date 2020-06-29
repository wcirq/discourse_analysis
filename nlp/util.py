# -*- coding: utf-8 -*- 
# @Time 2020/6/1 12:57
# @Author wcy
import os
import re
import numpy as np


def read_txt(filename_path):
    with open(filename_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        lines = [line.strip("\n") for line in lines]
    datas = "".join(lines)
    datas = re.split('[,。.，！!?？；;]', datas)
    return datas


def log_likelihood(l1, l2):
    """计算对数似然率"""
    if l2 == 0:
        l2 = 1e-9
    result = np.log(l1 / l2)
    return result
