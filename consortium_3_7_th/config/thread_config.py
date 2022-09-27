#!/usr/bin/env python
# _*_ coding: utf-8 _*_
"""
# @Time : 11/21/21 5:47 PM
# @Author : Archer
# @File : Thread_CONFIG.py
# @desc :
"""
import threading

from database.DatabaseOperation import th_DBOperation
from mine.pack_thread import Pack
from p2p.message_deal import mesaage_deal_th

CON = threading.Condition()




DB_THREAD = threading.Thread(target=th_DBOperation, name='thread_db')
DB_THREAD.start()

BLOCK_PACK = Pack()
BLOCK_PACK_THREAD = threading.Thread(target=BLOCK_PACK.run, name='thread_block')
BLOCK_PACK_THREAD.start()

MESSAGE_DEAL_THREAD = threading.Thread(target=mesaage_deal_th, name='mesaage_deal_th')
MESSAGE_DEAL_THREAD.start()

THREAD_POOL = []
THREAD_Pow = None
THREAD_Socket = None

if __name__ == '__main__':
    print('hello world')