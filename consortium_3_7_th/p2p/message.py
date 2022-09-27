#!/usr/bin/env python
# _*_ coding: utf-8 _*_
"""
# @Time : 11/22/21 5:23 PM
# @Author : Archer
# @File : message.py
# @desc :
"""
from config.config import LOGGER


class Message(object):
    def __init__(self):
        self.m = None
        self.m_hash = None
        self.sequence_number = None
        self.prepare_state = False
        self.commit_state = False
        self.pre_prepare_m = None
        self.tx_request = None
        self.prepare_m = []
        self.commit_m = []
        pass

    def txrequest(self, leader_node, sequence_number, m_hash, m):
        dict_ = {'sequence_number': sequence_number,
                 'm_hash': m_hash,
                 'm': m}
        self.m = m
        self.sequence_number = sequence_number
        self.m_hash = m_hash
        self.tx_request = dict_
        return self


    def preprepare(self, leader_node, sequence_number, m_hash, m):
        dict_ = {'leader_node': leader_node,
                 'sequence_number': sequence_number,
                 'm_hash': m_hash,
                 'm': m}
        self.m = m
        self.sequence_number = sequence_number
        self.m_hash = m_hash
        self.pre_prepare_m = dict_
        return self

    def prepare(self, leader_node, sequence_number, m_hash, sender_node):
        dict_ = {'leader_node': leader_node,
                 'sequence_number': sequence_number,
                 'm_hash': m_hash,
                 'sender_node': sender_node}
        if dict_ in self.prepare_m:
            LOGGER.info('prepare: \n' + str(dict_) + 'have received!')
        else:
            self.prepare_m.append(dict_)
        return self

    def commit(self, leader_node, sequence_number, m_hash, sender_node):
        dict_ = {'leader_node': leader_node,
                 'sequence_number': sequence_number,
                 'm_hash': m_hash,
                 'sender_node': sender_node}
        if dict_ in self.commit_m:
            LOGGER.info('commit: \n' + str(dict_) + 'have received!')
        else:
            self.commit_m.append(dict_)


if __name__ == '__main__':
    print('hello world')
