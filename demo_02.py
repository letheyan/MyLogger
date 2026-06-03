# Time: 2026/6/3 09:53         
# Author: 颜慧雍                   
# File: demo_02.py             
# Software: PyCharm
from src.yan_logger import MyLogger
import logging
from demo_01 import fun

ml = MyLogger("测试")

with ml.with_run_time():
    ml.info('info1')
    ml.disable_stream()
    ml.disable_file()
    ml.info('info22')
    ml.enable_stream()
    ml.enable_file("demo_02.txt")
    ml.info('info333')


# fun()
