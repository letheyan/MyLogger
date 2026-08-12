# Time: 2026/2/10 15:40         
# Author: 颜慧雍                   
# File: demo_01.py             
# Software: PyCharm

# from yan_logger import MyLogger
# import logging
from src.yan_logger import MyLogger


ml = MyLogger("测试", file_path="log.txt")

# ml.file_handler.setLevel(logging.ERROR)

ml.info('info1')
ml.info('info11')
ml.info('info111')
ml.stream_logger_level = 20
ml.print(ml.config)



def fun1():
    with ml.with_run_time():
        MyLogger.print("开始计时……")         # 集成实例静态print函数，增加显示文件名及行号。
        MyLogger.time.sleep(1)              # 类方法集成了sleep模块，不用多次导入。
        MyLogger.print("with 模块运行结束。")


@ml.run_time()
def fun2():
    MyLogger.print("开始计时……")         # 集成实例静态print函数，增加显示文件名及行号。
    MyLogger.time.sleep(2)              # 类方法集成了sleep模块，不用多次导入。
    MyLogger.print("with 模块运行结束。")

if __name__ == '__main__':
    fun1()
    fun2()


