# -*- coding: utf-8 -*- 
# @Time 2020/6/17 16:06
# @Author wcy
import os
import platform

system = platform.system()

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "./")
# 资源目录
RESOURCE_PATH = os.path.join(BASE_DIR, 'resources')
# 日志目录
LOGS_PATH = os.path.join(RESOURCE_PATH, 'logs', 'info.log')
# 索引目录
INDEX_ROOT_PATH = os.path.join(RESOURCE_PATH, 'indexs')
if not os.path.exists(INDEX_ROOT_PATH):
    os.mkdir(INDEX_ROOT_PATH)
# 分词字典
PHRASES_PATH = os.path.join(RESOURCE_PATH, 'phrases', 'phrases.txt')
if not os.path.exists(os.path.dirname(PHRASES_PATH)):
    os.mkdir(os.path.dirname(PHRASES_PATH))

# 数据路径
DATA_PATH = os.path.join(RESOURCE_PATH, 'data')


# 数据路径
if system == "Linux":
    pass
else:
    pass
