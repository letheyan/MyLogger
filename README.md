# MyLogger
Use Python's logging instead of print to quickly output program information to the screen and log files, distinguish information levels by color, and include the ability to calculate program runtime.
具备功能：
1. 支持不同日志等级以不同颜色输出。
2. 支持同时输出到屏幕及日志文件内。
3. 支持常用的日志设置。
4. 支持计算程序运行时间。
5. 支持原生print函数，附带文件名和行号。
# 快速使用

`pip install yan-logger`

```python
from yan-logger import MyLogger

mg = MyLogger()
mg.debug('debug')
mg.info('info')
mg.warning('warning')
mg.error('error')
mg.critical('critical')
```
运行结果：
包含 日志器名称、运行时间点、运行文件名、输出所在行号
<img width="690" height="281" alt="image" src="https://github.com/user-attachments/assets/0e304879-8c72-4881-996a-f897a1bbc463" />

# 进阶使用
```python
from yan-logger import MyLogger

mg = MyLogger("new_logger", file_path='log_demo.log')   # 自定义日志器名称，输出到屏幕且保存到log_demo.log文件中。  具体参数设置见源码。
mg.stream_logger_level= "warning"                       # 设置输出到屏幕的日志级别为"warning"
mg.file_logger_level = 20                               # 设置保存到日志文件的级别为 “info”， 级别设置用数字和单词均可。
mg.debug('debug')
mg.info('info')
mg.warning('warning')
mg.error('error')
mg.critical('critical')
```
运行结果：
在屏幕上只输出"warning" 级别以上的内容，在日志文件中是输出info级别内容。
<img width="652" height="167" alt="image" src="https://github.com/user-attachments/assets/adc59dba-c6fd-42ca-b80f-365bf9a1b3b1" />

**计算程序运行时间**
```python
from yan-logger import MyLogger

mg = MyLogger("new_logger")

# 方法一，用with mg.with_run_time()包裹需要计算的代码即可
with mg.with_run_time():
    for _ in range(3):
        mg.debug(_)
        mg.time.sleep(1)

# 方法二，使用装饰器mg.run_time(),默认参数1 只运行一遍函数。
@mg.run_time()
def fun():
    for _ in range(3):
        mg.debug(_)
        mg.time.sleep(1)

fun()
```
运行结果如下:

自动输出程序运行时间<br>
<img width="701" height="444" alt="image" src="https://github.com/user-attachments/assets/65e318ce-29fe-4b1e-8a54-c97d81abd418" />


