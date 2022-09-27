#!/usr/bin/env python
# _*_ coding: utf-8 _*_
"""
# @Time : 11/15/21 4:15 AM
# @Author : Archer
# @File : test.py
# @desc :
"""
import threading
import queue
import time

QUEST_QUEUE = queue.Queue(100)
ANSWER_QUEUE = queue.Queue(100)
LOCK_DB = threading.Lock()
th_sql = None
th_event = threading.Event()

def sql():
    while True:
        if QUEST_QUEUE.empty():
            th_event.clear()
            th_event.wait()
        data = QUEST_QUEUE.get()
        i = data[0]
        print('sql print: ', i)
        event = data[1]
        ANSWER_QUEUE.put(i)
        event.set()


def test(i):
    event = threading.Event()
    data = (i, event)
    QUEST_QUEUE.put(data)
    th_event.set()
    time.sleep(1)
    event.wait()
    result = ANSWER_QUEUE.get()
    print('test print: ', result)


if __name__ == '__main__':
    th_sql = threading.Thread(target=sql, name='thread_db')
    th_sql.start()
    for i in range(0, 5):
        th = threading.Thread(target=test, name='thread_db', args=(i,))
        th.run()