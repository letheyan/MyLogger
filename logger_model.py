# Time: 2026/2/6 15:28         
# Author: 颜慧雍                   
# File: log_model.py             
# Software: PyCharm    

import logging
import logging.handlers
from pathlib import Path
import sys
import copy
import time



# ANSI 转义序列用于设置颜色
class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[94m',  # 蓝色
        'INFO': '\033[92m',   # 绿色
        'WARNING': '\033[93m',  # 黄色
        'ERROR': '\033[91m',  # 红色
        'CRITICAL': '\033[35m',  # 加粗红色
        }
    RESET = '\033[0m'   # 重置颜色

    def format(self, record):
        levelname = record.levelname
        record_copy = copy.copy(record)   # 复制一份，使下面的颜色更改，不改变实际的record流属性。
        # levelname = record_copy.levelname

        if levelname in self.COLORS:
            record_copy.levelname = f"{self.COLORS[levelname]}{levelname}{self.RESET}"
            record_copy.msg = f"{self.COLORS[levelname]}{record_copy.msg}{self.RESET}"
        return super().format(record_copy)


class MyLogger:
    """自己封装的一个logger类，用来记录程序运行日志
           name：日志器的名称，默认__name__ = __main__。
           level：日志器报送等级，默认"DEBUG"为所有信息都报送。
           is_stream：是否输出到屏幕，默认True输出，False不输出。
           file_path:是否保存到文件，默认“None”-不写入文件。
                     如填文件路径 则保存到该文件，可以填写相对路径或绝对路径，路径目录不存在会自动创建。
           fh_fmt：写入到文件的日志格式，已设置默认。填写此参数，则会采用自定义的 Formatter。
           sh_fmt：控制台的日志输出格式，已设置默认。填写此参数，则会采用自定义的 Formatter。
           is_date：默认True，以日期循环的形式保存到文件中。False 以文件大小的形式循环保存。
       使用方法：
           1.普通使用，只输出到屏幕
               mg = MyLoger()
               mg.info("消息")
           2. 普通使用，不输出到屏幕，但保存到文件 logger.txt
                mg = MyLoger(is_stream=False, file_path="logger.txt")
                mg.file_logger_level = 'WARNING'  # 只保存'WARNING'及以上的消息。
                mg.error("消息")
       """

    level_dic ={"NOTSET":logging.NOTSET,
                "DEBUG":logging.DEBUG,
                "INFO":logging.INFO,
                'WARNING':logging.WARNING,
                "ERROR":logging.ERROR,
                "CRITICAL":logging.CRITICAL,
                "0": logging.NOTSET,
                "10": logging.DEBUG,
                "20": logging.INFO,
                '30': logging.WARNING,
                "40": logging.ERROR,
                "50": logging.CRITICAL
                }

    def __init__(self, name=__name__, level="DEBUG", is_stream=True, file_path=None, fh_fmt=None, sh_fmt=None,
                 is_date=True, when="d", interval=3, backup_count=100, max_bytes=10 * 1024 * 1024
                 ):
        """
         when：以日期循环的方式保存，参数有 'S' 秒，'M' 分钟，'H' 小时，'D' 天，'W0'-'W6' 工作日(0=星期一)。
         backupCount : 保存的文件个数，超过设置的数值，会清空前面的。如果为 0 ，则一直保存。
         max_bytes：以文件大小的方式进行保存，单位为字节。 10 * 1024 * 1024 = 10M。
        """
        self.logger = logging.getLogger(name)         # 创建日志器，自定义名称。默认为 __name__ 文件名。
        self.log_level=MyLogger.level_dic[str(level)]
        self.logger.setLevel(self.log_level)         # 初始日志级别，默认为10。
        self.formatter = "[logger:%(name)s | %(asctime)s | %(filename)s | %(lineno)d行]:\n%(levelname)s：%(message)s"
        self.stream_handler = None
        self.file_handler = None
        self.is_date = is_date
        self.when = when
        self.interval = interval
        self.backup_count = backup_count
        self.max_bytes = max_bytes
        self.make_sh_handler(is_stream, sh_fmt)        # 设置控制台的输出格式
        self.make_fh_handler(file_path, fh_fmt)

    # 输出到控制台（屏幕）
    def make_sh_handler(self, is_stream, sh_fmt):
        if is_stream:
            self.stream_handler = logging.StreamHandler(stream=sys.stdout)          # 创建日志处理器，在控制台打印
            _fm = sh_fmt if sh_fmt else self.formatter
            try:
                self.stream_handler.setFormatter(ColoredFormatter(_fm, datefmt='%Y-%m-%d %H:%M:%S'))  # 创建格式器，指定日志的打印格式，及日期格式
            except ValueError as e:
                self.logger.error(f"设置日志格式失败：{e}!!!")
                self.logger.error("启用默认输出格式。")
                _fmt = logging.Formatter(self.formatter, datefmt='%Y-%m-%d %H:%M:%S')
                self.stream_handler.setFormatter(fmt=_fmt)
            self.logger.addHandler(self.stream_handler)
        else:
            nu = logging.NullHandler()
            self.logger.addHandler(nu)
            print("不添加控制台输出。")

    # 读取屏幕输出的等级
    @property
    def stream_logger_level(self):
        if self.stream_handler:
            return self.stream_handler.level
        else:
            return "未创建输出到屏幕的handler。"

    # 设置屏幕输出的等级
    @stream_logger_level.setter
    def stream_logger_level(self, level):
        """单独调整屏幕输出的等级"""
        if self.stream_handler:
            self.stream_handler.setLevel(MyLogger.level_dic[str(level)])
        else:
            print("未创建输出到屏幕的handler。")

    # 输出到文件，永久保存。
    def make_fh_handler(self, file_path, fh_fmt=None):
        if file_path:
            file_path = Path(file_path)# 存储到文件
            print(Path(file_path).absolute())
            if not Path(file_path).parent.exists():
                Path(file_path).parent.mkdir(parents=True)

            # when='D', interval=30  每30天，创建一个文件。 backupCount=365 最多保存365个
            if self.is_date:
                self.file_handler = logging.handlers.TimedRotatingFileHandler(filename=file_path,
                                                                                   when=self.when,
                                                                                   interval=self.interval,
                                                                                   backupCount=self.backup_count,
                                                                                   encoding="utf-8")  # 创建日志处理器，用文件存放日志。
            else:
                self.file_handler = logging.handlers.RotatingFileHandler(filename=file_path,
                                                                              maxBytes=self.max_bytes, # 10MB
                                                                              backupCount=self.backup_count,
                                                                              encoding="utf-8")
            _fm = fh_fmt if fh_fmt else self.formatter
            _fmt = logging.Formatter(_fm, datefmt='%Y-%m-%d %H:%M:%S')
            self.file_handler.setFormatter(fmt=_fmt)
            self.logger.addHandler(self.file_handler)

    # 读取保存到文件的等级
    @property
    def file_logger_level(self):
        if self.file_handler:
            return self.file_handler.level
        else:
            return "未创建保存到文件的handler。"

    # 设置保存到文件的等级
    @file_logger_level.setter
    def file_logger_level(self, level):
        """单独调整屏幕输出的等级"""
        if self.file_handler:
            self.file_handler.setLevel(MyLogger.level_dic[str(level)])
        else:
            print("未创建保存到文件的handler。")

    # 显式代理最常用的方法（为了更好的IDE提示和类型检查）,与下面的def __getattr__(self, name)方法二选一
    # stacklevel表示：从当前帧（Logger.debug被调用处）向上跳过的帧数。设为2即跳过代理层 + Logger内部层，精准定位到用户代码。
    # def debug(self, msg, *args, **kwargs):
    #     kwargs['stacklevel'] = 2
    #     return self.logger.debug(msg, *args, **kwargs)
    #
    # def info(self, msg, *args, **kwargs):
    #     kwargs['stacklevel'] = 2
    #     return self.logger.info(msg, *args, **kwargs)
    #
    # def warning(self, msg, *args, **kwargs):
    #     kwargs['stacklevel'] = 2
    #     return self.logger.warning(msg, *args, **kwargs)
    #
    # def error(self, msg, *args, **kwargs):
    #     kwargs['stacklevel'] = 2
    #     return self.logger.error(msg, *args, **kwargs)
    #
    # def critical(self, msg, *args, **kwargs):
    #     kwargs['stacklevel'] = 2
    #     return self.logger.critical(msg, *args, **kwargs)

    def __getattr__(self, name):
         """将所有未定义的方法调用转发给内部的 logger 对象
            __getattr__ 的原理总结：
                查找顺序：是 Python 属性查找的最后一步
                触发条件：只在找不到属性/方法时才调用
                常见用途：实现动态属性、代理模式、惰性加载
                返回值：可以返回任何值，如果是方法应该返回可调用对象"""
         return getattr(self.logger, name)


    # 日志过滤器，暂未启用
    def _filter(self, result):
        if 'result' in result.msg:
            return False
        return True

    def run_time(self, repeat=1):
        """装饰器用法，计算函数的运行时间，repeat为重复运行次数,默认1次。
            用法： @run_time()
                  fun()             """
        def wraps_1(fun):
            def wraps_2(*args, **kwargs):
                a = time.perf_counter()
                for _ in range(repeat):
                    fun(*args, **kwargs)
                t = time.perf_counter()-a
                self.logger.debug(f"程序运行时间为：{t:.6} 秒。")
                return t
            return wraps_2
        return wraps_1

    def with_run_time(self):
        """with语句实现的计算程序运行时间。
             用法：  ml = MyLogger()               # 实例化一个对象。
                    with ml.with_run_time():      # 用with包裹即可。
             """
        class RunTime:
            def __init__(self2, logger):
                self2.start = time.perf_counter()
                self2.logger = logger

            def __enter__(self2):
                pass

            def __exit__(self2, exc_type, exc_val, exc_tb):
                self2.logger.debug(f"程序运行用时：{time.perf_counter()-self2.start:.6} 秒。")
                if exc_type:
                    print(f"捕获到异常：{exc_type}, {exc_val}")
        return RunTime(self.logger)

    # 等同print函数，只是增加了输出 文件名+行号。
    @staticmethod
    def print(*args,**kwargs):
        from builtins import print as _print
        s = f'{sys._getframe(1).f_lineno}'  # 注此处需加参数 1。
        return _print(f'【"{__name__}" 第{s}行】>:', *args, **kwargs)



if __name__ == '__main__':
    ml = MyLogger()
    # ml.stream_logger_level = 30
    # ml.file_logger_level = 30
    # ml.warning(ml.stream_logger_level)

    with ml.with_run_time():
        for i in range(5):
            ml.debug("哈哈哈哈")
            ml.info("呵呵呵")
            ml.warning("咯咯咯")
            ml.error("嗯嗯嗯")
            ml.critical("吼吼吼")
            # ml.logger.info(ml.stream_logger_level)
            ml.logger.debug("哈哈哈哈")
            ml.logger.info("呵呵呵")
            ml.logger.warning("咯咯咯")
            ml.logger.error("嗯嗯嗯")
            ml.logger.critical("吼吼吼")
            time.sleep(1)

    MyLogger.print("测试")

