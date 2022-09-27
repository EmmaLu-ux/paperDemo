#!/usr/bin/env python
# _*_ coding: utf-8 _*_
"""
# @Time : 12/16/21 9:51 PM
# @Author : Archer
# @File : database_message_create.py
# @desc :
"""
import threading

from config.config import DB_QUEST_QUEUE, DB_TH_EVENT


def construct_message(data, index):
    event = threading.Event()
    data_ = (data, index, event)
    DB_QUEST_QUEUE.put(data_)
    DB_TH_EVENT.set()
    return event



