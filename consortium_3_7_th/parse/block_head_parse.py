#!/usr/bin/env python
# _*_ coding: utf-8 _*_
"""
# @Time : 11/5/21 6:31 PM
# @Author : Archer
# @File : block_header_parse.py
# @desc :
"""
from tools.utils import *


class BlockHeadParse:
    def __init__(self):
        self.version = None
        self.block_height = None
        self.prev_block_hash = None
        self.tx_root = None
        self.state_root = None
        self.timestamp = None
        self.block_height = None
        self.raw_data = None
        self.block_hash = None

    def parser(self, raw_data):
        self.raw_data =raw_data
        self.block_hash = double_sha256(self.raw_data)
        self.raw_data = raw_data
        offset = 0
        self.version = decode_uint32(raw_data[offset:offset+8])
        offset += 8
        self.prev_block_hash = format_hash(raw_data[offset: offset+64])
        offset += 64
        print(self.prev_block_hash)
        self.block_height = decode_uint32(raw_data[offset: offset+8])
        print(raw_data[offset: offset:8])
        offset += 8
        self.state_root = format_data(raw_data[offset: offset+64])
        offset += 64
        self.tx_root = format_data(raw_data[offset: offset+64])
        offset += 64
        self.timestamp = decode_uint32(raw_data[offset: offset+8])
        offset += 8
        return self
        len_ = len(raw_data)
        a = 1

if __name__ == '__main__':
    raw_data = '0000000000000000000000000000000000000000000000000000000000000000000000000000000056510933f0878820defaaf25a6127a964da4250b005eaf5ca35795cba9ab4836474be5f76a1898b6684e37e2623543900e30cbb332917e97353087aebfb13b7614e48461'
    BlockHeadParse().parser(raw_data=raw_data)