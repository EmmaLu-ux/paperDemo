#!/usr/bin/env python
# _*_ coding: utf-8 _*_
"""
# @Time : 2/28/22 2:54 AM
# @Author : Archer
# @File : pack_thread.py
# @desc :
"""
import time

from config.config import BLOCK_INTERNAL_TIME
from mine.block import Block


class Pack:
    def __init__(self):
        self._running = False

    def terminate(self):
        self._running = False

    def run(self):
        while self._running:
            block = Block().construct()
            block.store_in_database()
            time.sleep(BLOCK_INTERNAL_TIME)
