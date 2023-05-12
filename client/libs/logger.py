import os
import time

class logger:
    os.makedirs(os.path.dirname(__file__) + '/logs', exist_ok=True)
    logfile = os.path.join(os.path.dirname(__file__) + '/logs', time.strftime("%Y-%m-%d %H-%M-%S", time.localtime()) + ".log")
    enable = False
    f = open(logfile, "w")

    def log(cls, msg):
        if(cls.enable):
            cls.f.write(time.strftime("%Y/%m/%d-%H:%M:%S", time.localtime()) + " \t " + str(msg) + "\r\n")
        return msg

    def lines(cls, n = 1):
        if(cls.enable):
            cls.f.write("\r\n" * n)

    def separator(cls, n = 50):
        if(cls.enable):
            cls.f.write("-" * n + "\r\n")

    def breakline(cls, n = 50):
        if(cls.enable):
            cls.f.write("\r\n" + "=" * n + "\r\n\r\n")

    def enable(cls):
        cls.enable = True

    def disable(cls):
        cls.enable = False

    def __del__(cls):
        cls.f.close()