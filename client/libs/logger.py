import os
import time

class logger:
    os.makedirs(os.path.dirname(__file__) + '/logs', exist_ok=True)
    logfile = os.path.join(os.path.dirname(__file__) + '/logs', time.strftime("%Y-%m-%d %H-%M-%S", time.localtime()) + ".log")
    enable = False
    f = open(logfile, "w")

    @classmethod
    def log(cls, msg):
        print(str(msg))
        if(cls.enable):
            cls.f.write(time.strftime("%Y/%m/%d-%H:%M:%S", time.localtime()) + " \t " + str(msg) + "\r\n")
        return msg

    @classmethod
    def lines(cls, n = 1):
        if(cls.enable):
            cls.f.write("\r\n" * n)

    @classmethod
    def separator(cls, n = 50):
        if(cls.enable):
            cls.f.write("-" * n + "\r\n")

    @classmethod
    def breakline(cls, n = 50):
        if(cls.enable):
            cls.f.write("\r\n" + "=" * n + "\r\n\r\n")

    @classmethod
    def enable(cls):
        cls.enable = True

    @classmethod
    def disable(cls):
        cls.enable = False

    @classmethod
    def __del__(cls):
        cls.f.close()