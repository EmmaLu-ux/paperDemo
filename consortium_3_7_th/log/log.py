#!/usr/bin/env python
# _*_ coding: utf-8 _*_
"""
# @Time : 11/15/21 7:05 PM
# @Author : Archer
# @File : log_test.py
# @desc :
"""
import logging
import os


def init_log():
    logger = logging.getLogger()
    # logging.basicConfig(level=logging.DEBUG)

    logger.setLevel(level=logging.DEBUG)  # Log等级总开关  此时是INFO

    pwd = os.getcwd()
    pwd = pwd[:pwd.rfind('/')]
    # 第二步，创建一个handler，用于写入日志文件
    # logfile_path = pwd + '/log/my.log'
    logfile_path = pwd + '/log/my.log'
    fh = logging.FileHandler(logfile_path, mode='a')  # open的打开模式这里可以进行参考
    fh.setLevel(logging.DEBUG)  # 输出到file的log等级的开关

    # 第三步，再创建一个handler，用于输出到控制台
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)  # 输出到console的log等级的开关

    # 第四步，定义handler的输出格式（时间，文件，行数，错误级别，错误提示）
    formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # 第五步，将logger添加到handler里面
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger

    # # 日志级别
    # logger.debug('这是 logger debug message')
    # logger.info('这是 logger info message')
    # logger.warning('这是 logger warning message')
    # logger.error('这是 logger error message')
    # logger.critical('这是 logger critical message')


if __name__ == '__main__':
    log = init_log()
