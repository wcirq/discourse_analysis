# -*- coding: utf-8 -*- 
# @Time 2020/6/18 16:35
# @Author wcy
import logging.handlers
import os

from config import LOGS_PATH

if not os.path.exists(os.path.dirname(LOGS_PATH)):
    os.mkdir(os.path.dirname(LOGS_PATH))
logger = logging.getLogger(__name__)
logger.setLevel(level = logging.INFO)
handler = logging.handlers.TimedRotatingFileHandler(LOGS_PATH, when='H', interval=6, backupCount=40, encoding="utf-8")
handler.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s][%(filename)s][%(funcName)s][line:%(lineno)d][%(levelname)s] %(message)s')
handler.setFormatter(formatter)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formatter)

logger.addHandler(handler)
logger.addHandler(console)
