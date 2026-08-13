# Time: 2026/2/6 15:28         
# Author: lethe_yan
# File: log_model.py             
# Software: PyCharm    

import logging
import logging.handlers
from pathlib import Path
import sys
import copy
import time
from functools import wraps
import threading


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
               mg = MyLogger()
               mg.info("消息")
           2. 普通使用，不输出到屏幕，但保存到文件 logger.txt
                mg = MyLogger(is_stream=False, file_path="logger.txt")
                mg.file_logger_level = 'WARNING'  # 只保存'WARNING'及以上的消息。
                mg.error("消息")
       """
    _lock = threading.Lock()
    _instances = {}  # 缓存实例 {name: instance}
    _initialized = set()
    _configs = {}  # 存储每个 name 的配置 {name: config_dict}

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

    time = time

    def __new__(cls, name=__name__, *args, **kwargs):
        if name in cls._instances:
            return cls._instances[name]
        instance = super().__new__(cls)
        cls._instances[name] = instance
        return instance


    def __init__(self, name=__name__, level="DEBUG", is_stream=True, file_path:str=None, fh_fmt=None, sh_fmt=None,
                 is_date=True, when="d", interval=7, backup_count=100, max_bytes=5 * 1024 * 1024
                 ):
        """
         is_date：默认True，以日期循环的方式进行存储
         interval：默认7，7天一个文件。
         when：以日期循环的方式保存，参数有 'S' 秒，'M' 分钟，'H' 小时，'D' 天，'W0'-'W6' 工作日(0=星期一)。
         backupCount : 保存的文件个数，超过设置的数值，会清空前面的。如果为 0 ，则一直保存。
         max_bytes：以文件大小的方式进行保存，单位为字节。 5 * 1024 * 1024 = 5M。
        """
        with MyLogger._lock:
            if name in MyLogger._initialized:
                # 已经存在的实例，只需要拿到已有的 logger 对象即可
                self.logger = logging.getLogger(name)
                self.logger.propagate = False
                # MyLogger.print("已经存在的实例")
                # 可以跳过后续所有属性初始化
                self.stream_handler = None
                self.file_handler = None
                # 尝试从已有的 handlers 中恢复 stream_handler 和 file_handler 引用
                for h in self.logger.handlers:
                    if isinstance(h, logging.StreamHandler) and not isinstance(h,
                                                                               (logging.handlers.TimedRotatingFileHandler,
                                                                                logging.handlers.RotatingFileHandler)):
                        self.stream_handler = h
                    elif isinstance(h, (logging.handlers.TimedRotatingFileHandler, logging.handlers.RotatingFileHandler)):
                        self.file_handler = h

                if not any(isinstance(h, logging.NullHandler) for h in self.logger.handlers):
                    self._null_handler = logging.NullHandler()
                    self.logger.addHandler(self._null_handler)


                self.name = name
                self.config:dict = MyLogger._configs.get(self.name)
                # MyLogger.print(self.config)
                self.formatter = self.config.get('formatter')
                self.is_stream = self.config.get('is_stream')
                self.file_path = self.config.get('file_path')
                self.is_date = self.config.get('is_date')
                self.when = self.config.get('when')
                self.interval = self.config.get('interval')
                self.backup_count = self.config.get('backup_count')
                self.max_bytes = self.config.get('max_bytes')
                self.sh_fmt = self.config.get('sh_fmt')
                self.sh_level = self.config.get('sh_level')
                self.fh_fmt = self.config.get('fh_fmt')
                self.fh_level = self.config.get('fh_level')

                if ((level != "DEBUG") or (is_stream != True) or (file_path is not None) or (fh_fmt is not None)
                        or (sh_fmt is not None) or (is_date != True) or (when != "d") or (interval != 7) or
                        (backup_count != 100) or (max_bytes != 5 * 1024 * 1024)):
                    self.logger.warning("已有同名的MyLogger实例，初始化时无需传入name之外的参数。如需重新设置，请使用set_config()方法。", stacklevel=2)
                return


            MyLogger._initialized.add(name)
            self.name = name
            self.logger = logging.getLogger(name)     # 创建日志器，自定义名称。默认为 __name__ 文件名。
            self.logger.propagate = False
            self._null_handler = logging.NullHandler()
            self.logger.addHandler(self._null_handler)

            self.log_level=str(level).upper()
            if self.log_level not in MyLogger.level_dic:
                self.logger.warning(f"无效的日志等级 '{level}'，已使用默认级别 DEBUG")
                self.log_level = 'DEBUG'

            self.logger.setLevel(MyLogger.level_dic[self.log_level])    # 初始日志级别，默认为10。
            self.formatter = "[logger:%(name)s | %(asctime)s | %(filename)s | %(lineno)d行]:\n%(levelname)s：%(message)s"
            self.stream_handler = None
            self.sh_fmt = sh_fmt
            self.file_handler = None
            self.fh_fmt = fh_fmt
            self.is_date = is_date
            self.when = when
            self.interval = interval
            self.backup_count = backup_count
            self.max_bytes = max_bytes


            # 把参数存入到类属性中，方便后续调用。
            self.config = MyLogger._configs.setdefault(name, {})
            self.config.update({
                'log_level':self.log_level,
                'formatter': self.formatter,
                'is_stream': is_stream,
                'file_path': file_path,
                'is_date': is_date,
                'when': when,
                'interval': interval,
                'backup_count': backup_count,
                'max_bytes': max_bytes,
                'sh_fmt': sh_fmt,
                'sh_level': None,
                'fh_fmt': fh_fmt,
                'fh_level': None
            })

            self.make_sh_handler(is_stream, sh_fmt)  # 创建控输出到制台的handler
            self.make_fh_handler(file_path, fh_fmt, is_date, when, interval, backup_count, max_bytes)  # 创建保存到文件的handler

            if not self.logger.handlers:
                self.logger.warning("当前 Logger 未配置任何输出目标（控制台和文件均已禁用），日志将不会被记录。")

    # 批量设置属性的方法
    def set_config(self,sh_level=None, is_stream=None, fh_level=None, file_path=None, fh_fmt=None, sh_fmt=None,
                 is_date=None, when=None, interval=None, backup_count=None, max_bytes=None):

        # 新方式设置sh_handler
        if sh_level is not None:
            self.sh_level = sh_level
            self.config['sh_level'] = sh_level
        else:
            self.sh_level = self.config['sh_level']

        if sh_fmt is not None:
            self.sh_fmt = sh_fmt
            self.config['sh_fmt'] = sh_fmt
        else:
            self.sh_fmt = self.config['sh_fmt']

        if is_stream is not None:
            self.is_stream = is_stream
            self.config['is_stream'] = is_stream
        else:
            self.is_stream = self.config['is_stream']

        sh_changed = (sh_level is not None) or (sh_fmt is not None) or (is_stream is not None)

        if sh_changed:
            if self.is_stream:
                # self.logger.info("123")
                self.disable_stream()
                self.enable_stream(level=self.sh_level, sh_fmt=self.sh_fmt)
            else:
                # self.logger.info("456")
                self.disable_stream()

        # 设置fh_handler，已做好传入参数和配置参数的选择
        if fh_level is not None:
            self.fh_level = fh_level
            self.config['fh_level'] = fh_level
        else:
            self.fh_level = self.config['fh_level']

        if file_path is not None:
            self.file_path = file_path
            self.config['file_path'] = file_path
        else:
            self.file_path = self.config['file_path']

        if fh_fmt is not None:
            self.fh_fmt = fh_fmt
            self.config['fh_fmt'] = fh_fmt
        else:
            self.fh_fmt = self.config['fh_fmt']

        if is_date is not None:
            self.is_date = is_date
            self.config['is_date'] = is_date
        else:
            self.is_date = self.config['is_date']

        if when is not None:
            self.when = when
            self.config['when'] = when
        else:
            self.when = self.config['when']

        if interval is not None:
            self.interval = interval
            self.config['interval'] = interval
        else:
            self.interval = self.config['interval']

        if backup_count is not None:
            self.backup_count = backup_count
            self.config['backup_count'] = backup_count
        else:
            self.backup_count = self.config['backup_count']

        if max_bytes is not None:
            self.max_bytes = max_bytes
            self.config['max_bytes'] = max_bytes
        else:
            self.max_bytes = self.config['max_bytes']

        fh_changed = ((fh_level is not None) or (file_path is not None) or (fh_fmt is not None) or (is_date is not None) or
                      (when is not None) or (interval is not None) or (backup_count is not None) or (max_bytes is not None))

        # 如果有传入file_path参数
        if fh_changed:
            # 当file_path为空时，关闭
            if self.file_path :
                self.disable_file()
                self.enable_file(self.fh_level, self.file_path, self.fh_fmt, self.is_date, self.when, self.interval,
                                 self.backup_count, self.max_bytes)
            else:
                self.disable_file()

    # 输出到控制台（屏幕）
    def make_sh_handler(self, is_stream, sh_fmt=None):
        # 同步到配置属性中
        self.config['is_stream'] = is_stream
        if is_stream:
            self.stream_handler = logging.StreamHandler(stream=sys.stdout)          # 创建日志处理器，在控制台打印
            # _fm = sh_fmt if (sh_fmt is not None) else self.formatter
            if sh_fmt:
                _fm = sh_fmt
                self.config['sh_fmt'] = _fm   # 同步到配置属性中
            else:
                if self.config["sh_fmt"]:
                    _fm = self.config["sh_fmt"]
                else:
                    _fm = self.config["formatter"]
            try:
                self.stream_handler.setFormatter(ColoredFormatter(_fm, datefmt='%Y-%m-%d %H:%M:%S'))  # 创建格式器，指定日志的打印格式，及日期格式
            except ValueError as e:
                self.logger.error(f"设置日志格式失败：{e}!!!")
                self.logger.error("启用默认输出格式。")
                _fmt = logging.Formatter(self.formatter, datefmt='%Y-%m-%d %H:%M:%S')
                self.stream_handler.setFormatter(fmt=_fmt)
            self.logger.addHandler(self.stream_handler)
        else:
            # nu = logging.NullHandler()
            # self.logger.addHandler(nu)
            self.logger.debug("不添加控制台输出。")

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
            if str(level).upper() in MyLogger.level_dic:
                self.stream_handler.setLevel(MyLogger.level_dic[str(level).upper()])
                MyLogger.print(f"已设置日志等级：{MyLogger.level_dic.get(str(level).upper())}")
                self.config['sh_level'] = level   # 更新配置
            else:
                self.logger.warning(f"请输入正确的日志等级：{MyLogger.level_dic.keys()}，现采用默认的日志等级debug。")
        else:
            self.logger.info("未创建输出到屏幕的handler。")

    def disable_stream(self):
        """禁用屏幕输出"""
        if self.stream_handler is not None:
            self.logger.debug("关闭输出到屏幕。",stacklevel=2)
            self.logger.removeHandler(self.stream_handler)
            self.stream_handler.close()
            self.stream_handler = None
            self.config['is_stream'] = False

    def enable_stream(self, level=None, sh_fmt=None):
        if self.stream_handler is None:
            self.make_sh_handler(True, sh_fmt)
            self.logger.debug("启用输出到屏幕。", stacklevel=2)
            if level:
                self.stream_logger_level = level
                self.config["sh_level"] = level  # 更新配置
            else:
                if self.config["sh_level"]:
                    self.stream_logger_level = self.config["sh_level"]
                else:
                    self.stream_logger_level = self.config["log_level"]
        else:
            self.logger.info("已开启输出到屏幕，无需重新开启。")


    # 输出到文件，永久保存。
    def make_fh_handler(self, file_path:str, fh_fmt, is_date, when, interval, backup_count, max_bytes):
        if self.file_handler:
            self.logger.error("file_handler已创建，请勿调用该方法再次创建。")
            return

        self.file_path = file_path if file_path else self.config['file_path']
        if self.file_path:
            try:
                file_path = Path(self.file_path)    # 存储到文件
                # MyLogger.print(Path(file_path).absolute())
                if not file_path.parent.exists():    # 先检查有没父目录，没的话，创建
                    file_path.parent.mkdir(parents=True)
            except Exception as e:
                self.logger.error(e, exc_info=True)
                self.logger.warning("【临时性采用当前目录进行存储log.txt】")
                self.file_path = "log.txt"
                file_path = Path(self.file_path)

            # when='D', interval=3  每3天，创建一个文件。 backupCount=100 最多保存100个
            if is_date:
                try:
                    interval = int(interval)
                    if interval < 1:
                        raise ValueError
                except (ValueError, TypeError):
                    self.logger.warning("interval 非法，已使用默认值 1")
                    interval = 1

                self.file_handler = logging.handlers.TimedRotatingFileHandler(filename=file_path,
                                                                              when=when,
                                                                              interval=interval,
                                                                              backupCount=backup_count,
                                                                              encoding="utf-8")  # 创建日志处理器，用文件存放日志。
            else:
                if max_bytes <= 0:
                    self.logger.warning("max_bytes 必须大于0，已设为默认 5MB")
                    max_bytes = 5 * 1024 * 1024
                self.file_handler = logging.handlers.RotatingFileHandler(filename=file_path,
                                                                         maxBytes=max_bytes, # 5MB
                                                                         backupCount=backup_count,
                                                                         encoding="utf-8")
            # _fm = fh_fmt if fh_fmt else self.formatter
            if fh_fmt:
                _fm = fh_fmt

            else:
                if self.config['fh_fmt']:
                    _fm = self.config['fh_fmt']
                else:
                    _fm = self.formatter

            # 同步到配置属性中
            self.config['file_path'] = self.file_path
            self.config['fh_fmt'] = _fm
            self.config['is_date'] = is_date
            self.config['when'] = when
            self.config['interval'] = interval
            self.config['backup_count'] = backup_count
            self.config['max_bytes'] = max_bytes

            _fmt = logging.Formatter(_fm, datefmt='%Y-%m-%d %H:%M:%S')
            self.file_handler.setFormatter(fmt=_fmt)
            self.logger.addHandler(self.file_handler)
        else:
            self.logger.debug("无日志保存路径，不开启保存到本地文件的日志功能。", stacklevel=3)

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
        """单独调整保存到文件的日志等级"""
        if self.file_handler:
            if str(level).upper() in MyLogger.level_dic:
                self.file_handler.setLevel(MyLogger.level_dic[str(level).upper()])
                MyLogger.print(f"已设置日志等级：{MyLogger.level_dic.get(str(level).upper())}")
                self.config['fh_level'] = level   # 更新配置
        else:
            self.logger.info("未创建保存到文件的handler。")

    def disable_file(self):
        """禁用保存到文件"""
        if self.file_handler is not None:
            self.logger.debug("关闭保存到本地日志功能。", stacklevel=2)
            self.logger.removeHandler(self.file_handler)
            self.file_handler.close()
            self.file_handler = None
            self.config['file_path'] = None

    def enable_file(self, level=None, file_path=None, fh_fmt=None, is_date=None, when=None,
                          interval=None,  backup_count=None, max_bytes=None):

        if self.file_handler is None:
            self.logger.debug("开启保存到本地日志功能。", stacklevel=2)
            if not file_path and not self.config["file_path"]:
                self.file_path = "log.txt"
                self.logger.warning(f"未输入保存的logger文件名或路径，默认保存到当前目录的{self.file_path}文件中。")
            else:
                self.file_path = file_path or self.config["file_path"]

            self.fh_fmt = fh_fmt if (fh_fmt is not None) else (self.config.get("fh_fmt") or self.config.get("formatter"))

            self.is_date = is_date if (is_date is not None) else self.config.get("is_date", True)

            self.when = when if (when is not None) else self.config.get("when", "d")

            self.interval = interval if (interval is not None) else self.config.get("interval", 7)

            self.backup_count = backup_count if (backup_count is not None) else self.config.get("backup_count", 100)

            self.max_bytes = max_bytes if (max_bytes is not None) else self.config.get("max_bytes", 5*1024*1024)

            self.make_fh_handler(self.file_path, self.fh_fmt, self.is_date, self.when, self.interval, self.backup_count, self.max_bytes)

            if level is not None:
                self.file_logger_level = level
            else:
                saved = self.config.get("fh_level")
                self.file_logger_level = saved if saved else self.config.get("log_level", "DEBUG")
        else:
            self.logger.info("已开启保存到文件，无需重新开启。")

    def debug(self, msg, *args, **kwargs):
        """记录 DEBUG 级别日志"""
        self.logger.log(logging.DEBUG, msg, *args, stacklevel=2, **kwargs)

    def info(self, msg, *args, **kwargs):
        """记录 INFO 级别日志"""
        self.logger.log(logging.INFO, msg, *args, stacklevel=2, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """记录 WARNING 级别日志"""
        self.logger.log(logging.WARNING, msg, *args, stacklevel=2, **kwargs)

    def error(self, msg, *args, **kwargs):
        """记录 ERROR 级别日志"""
        self.logger.log(logging.ERROR, msg, *args, stacklevel=2, **kwargs)

    def critical(self, msg, *args, **kwargs):
        """记录 CRITICAL 级别日志"""
        self.logger.log(logging.CRITICAL, msg, *args, stacklevel=2, **kwargs)

    def exception(self, msg, *args, **kwargs):
        """记录异常日志（自动附带 traceback）"""
        kwargs.setdefault('exc_info', True)
        self.logger.log(logging.ERROR, msg, *args, stacklevel=2, **kwargs)

    def log(self, level, msg, *args, **kwargs):
        """记录指定级别日志"""
        self.logger.log(level, msg, *args, stacklevel=2, **kwargs)

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
            @wraps(fun)
            def wraps_2(*args, **kwargs):
                a = time.perf_counter()
                for _ in range(repeat):
                    fun(*args, **kwargs)
                t = time.perf_counter()-a
                self.logger.info(f"程序运行时间为：{t:.6} 秒。", stacklevel=2)
                return t
            return wraps_2
        return wraps_1

    def with_run_time(self):
        """with语句实现的计算程序运行时间。
             用法：  ml = MyLogger()               # 实例化一个对象。
                    with ml.with_run_time():      # 用with包裹即可。
             """
        class RunTime:
            def __init__(self, logger):
                self.start = time.perf_counter()
                self.logger = logger

            def __enter__(self):
                pass

            def __exit__(self, exc_type, exc_val, exc_tb):
                self.logger.info(f"程序运行用时：{time.perf_counter()-self.start:.6} 秒。", stacklevel=3)
                if exc_type:
                    print(f"捕获到异常：{exc_type}, {exc_val}")
        return RunTime(self.logger)

    # 等同print函数，只是增加了输出 文件名+行号。
    @staticmethod
    def print(*args,**kwargs):
        # from builtins import print as _print
        caller_frame = sys._getframe(1) # 注此处需加参数 1。
        row = f'{caller_frame.f_lineno}'
        caller_name = Path(caller_frame.f_code.co_filename).name
        return print(f'【"{caller_name}" 第{row}行】>:', *args, **kwargs)

if __name__ == '__main__':
    # 测试1：初始化时级别是否生效
    ml = MyLogger(level=10)
    ml.debug("这条应该显示（修复前可能不显示）")

    with ml.with_run_time():
        MyLogger.print("开始计时……")         # 集成实例静态print函数，增加显示文件名及行号。
        MyLogger.time.sleep(1)              # 类方法集成了sleep模块，不用多次导入。
        MyLogger.print("with 模块运行结束。")

    # 测试2：关闭后再开启，级别是否保持
    ml.disable_stream()
    ml.warning("这条不该显示111")
    ml.enable_stream()
    ml.debug("重新开启后，这条应该显示，且级别应为DEBUG")

    # 测试3：动态调级
    ml.set_config(is_stream=True, sh_level="ERROR")
    ml.info("这条不该显示222")
    ml.error("这条应该显示333")

    # 测试4：set_config开启并指定级别
    ml.set_config(is_stream=False)
    ml.set_config(is_stream=True, sh_level="WARNING")
    ml.info("不该显示444")
    ml.warning("应该显示555")



