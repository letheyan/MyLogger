# Time: 2026/2/10 15:40         
# Author: 颜慧雍                   
# File: demo_01.py             
# Software: PyCharm

# from yan_logger import MyLogger
from src.yan_logger import MyLogger


ml = MyLogger()

ml.info('info')

with ml.with_run_time():
    MyLogger.print("开始计时……")         # 集成实例静态print函数，增加显示文件名及行号。
    MyLogger.time.sleep(3)              # 类方法集成了sleep模块，不用多次导入。
    MyLogger.print("with 模块运行结束。")


