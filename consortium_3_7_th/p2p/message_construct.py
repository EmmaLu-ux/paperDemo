#!/usr/bin/env python
# _*_ coding: utf-8 _*_
"""
# @Time : 2/27/22 11:37 PM
# @Author : Archer
# @File : message_construct.py
# @desc :
"""
from config.config import NODE_INFO
from tools.jsonOp import file2json


def tx_broad_message(tx):
    m = {
        "m_file": {'file_path': tx.data['file_path'],
                   'file_data': file2json(tx.data['file_path'])},
        "m_data": {'tx_raw_data': tx.raw_data}
    }
    message = {
        "m_type": "tx_broadcast",
        "i": NODE_INFO,

        "m_hash": tx.tx_hash,
        "m": m
    }
    return message


def tx_request_message(tx_hash):
    message = {'m_type': 'tx_request',
               'm_hash': tx_hash,
               'i': NODE_INFO}
    return message


def pre_prepare_message(block_head, block_tx_hash_list, m_hash, leader_node, sequence_number):
    m = {'m_data': {'block_head': block_head,
                    'block_tx_hash_list': block_tx_hash_list},
         'm_hash': m_hash
         }
    message = {'m_type': 'pre-prepare',
               'm_hash': m_hash,
               'v': leader_node,
               'n': sequence_number,
               'i': NODE_INFO,
               'm': m
               }
    return message


def prepare_message(m_hash, leader_node, sequence_number):
    message = {'m_type': 'prepare',
               'm_hash': m_hash,
               'v': leader_node,
               'n': sequence_number,
               'i': NODE_INFO}
    return message


def commit_message(m_hash, leader_node, sequence_number):
    message = {'m_type': 'commit',
               'm_hash': m_hash,
               'v': leader_node,
               'n': sequence_number,
               'i': NODE_INFO}
    return message


if __name__ == '__main__':
    print('hello world')
