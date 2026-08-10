# Time: 2026/6/3 09:53         
# Author: 颜慧雍                   
# File: demo_02.py             
# Software: PyCharm
from src.yan_logger import MyLogger
from demo_01 import fun1

ml = MyLogger("测试")
ml.set_config(sh_level=10, file_path="log.txt")


ml.print(ml.config)


fun1()

def fun2():
    with ml.with_run_time():
        ml.critical('info1')
        ml.disable_stream()
        ml.info('info22')
        ml.enable_stream(level=20)
        # ml.disable_file()
        ml.info('info333')
