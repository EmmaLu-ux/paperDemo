#!/usr/bin/env python
# _*_ coding: utf-8 _*_
"""
# @Time : 9/21/21 11:23 PM
# @Author : Archer
# @File : init.py
# @desc :
"""
from config.config import *
from p2p.node import Node


def create_node():
    NODE = Node(NODE_INFO['ip'], NODE_INFO['port'])
    NODE.start()


def connect_node():
    for node_ in NODE_LIST:
        if NODE_INFO != node_:
            NODE.connect_with_node(node_['ip'], node_['port'])
            LOGGER.info(NODE_INFO + 'connect with ' + str(node_) + 'successfully!')


if __name__ == '__main__':
    a = 1
