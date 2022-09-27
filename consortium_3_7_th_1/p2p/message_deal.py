#!/usr/bin/env python
# _*_ coding: utf-8 _*_
"""
# @Time : 11/21/21 7:11 PM
# @Author : Archer
# @File : message_deal.py
# @desc :
"""

from config.config import *
from database.database_message_create import construct_message
from p2p.message import Message
from p2p.message_construct import tx_request_message, tx_broad_message, prepare_message, commit_message
from parse.block_parse import BlockParse
from parse.transaction_parse import TransactionParse
from tools.jsonOp import json2file, path_create, file2json


def mesaage_deal_th():
    while True:
        if MESSAGE_QUEUE.empty():
            MESSAGE_TH_EVENT.clear()
            MESSAGE_TH_EVENT.wait()
        message = MESSAGE_QUEUE.get()

        message_deal(message)


def message_deal(message):
    MESSAGES = update()
    if message['m_type'] == 'tx_broadcast':
        # client or user broadcasts new tx.
        # node receives the tx and check it, the tx will be selected into tx pool.
        tx_raw_data = message['m']['m_data']['tx_raw_data']
        tx = TransactionParse().parse(tx_raw_data)
        # check signature
        if not tx.signature_verify():
            m = tx.tx_hash + ' verify failed'
            LOGGER.error(m)
            return
        if tx.check_if_stored():
            m = tx.tx_hash + ' already been stored'
            LOGGER.error(m)
            return
        if tx.version == 2:
            # create contract
            addr = tx.tx_hash
            dir_ = '/transaction_file/revoke_contract_log/' + str(addr)
            path_create(dir_)
            json2file(message['m']['m_file']['file_path'], message['m']['m_file']['file_data'])
        elif tx.version == 3:
            # invoke contract
            if message['m']['m_file']['file_path'] != '':
                json2file(message['m']['m_file']['file_path'], message['m']['m_file']['file_data'])
        tx.store_in_database()
        m = tx.tx_hash + 'store successfully!'
        LOGGER.info(m)
    elif message['m_type'] == 'tx_request':
        # request for tx
        tx_hash = message['m_hash']
        sender_node = NODE.find_node(message['i']['port'])
        if sender_node is None:
            print('do not find the connect thread')
        # search tx_raw_data
        data = {'tx_hash': tx_hash}
        event = construct_message(data=data, index=18)
        event.wait()
        tx_raw_data = DB_ANSWER_QUEUE.get()
        tx = TransactionParse().parse(tx_raw_data)
        # check file
        message_ = tx_broad_message(tx)
        print('message:', message_)
        NODE.send_to_node(sender_node, message_)

    elif message['m_type'] == 'pre-prepare':
        # leader pack a new block and send pre-prepare.
        m_hash = message['m_hash']
        sequence_number = message['n']
        m = message['m']
        leader_node = message['v']
        MESSAGES[m_hash] = Message().preprepare(leader_node=leader_node, sequence_number=sequence_number, m_hash=m_hash,
                                                m=m)
        block_head_raw_data = message['m']['m_data']['block_head']
        block_tx_hash_list = message['m']['m_data']['block_tx_hash_list']

        # consensus all packed tx
        tx_consensus(block_tx_hash_list, leader_node)

        message_ = prepare_message(m_hash, leader_node, sequence_number)
        NODE.send_to_nodes(message_)
    elif message['m_type'] == 'prepare':
        m_hash = message['m_hash']
        sequence_number = message['n']
        leader_node = message['v']
        sender_node = message['i']
        if m_hash not in MESSAGES:
            MESSAGES[m_hash] = Message().prepare(leader_node=leader_node, sequence_number=sequence_number,
                                                 m_hash=m_hash,
                                                 sender_node=sender_node)
        else:
            MESSAGES[m_hash].prepare(leader_node=leader_node, sequence_number=sequence_number, m_hash=m_hash,
                                     sender_node=sender_node)
        if message['v'] == NODE_INFO:
            verify_limit = VERIFY_LIMIT - 1
        else:
            verify_limit = VERIFY_LIMIT
        if not MESSAGES[m_hash].prepare_state and len(MESSAGES[m_hash].prepare_m) >= verify_limit:
            MESSAGES[m_hash].prepare_state = True
            message_ = commit_message(m_hash, leader_node, sequence_number)
            NODE.send_to_nodes(message_)
        pass
    elif message['m_type'] == 'commit':
        m_hash = message['m_hash']
        sequence_number = message['n']
        leader_node = message['v']
        sender_node = message['i']
        MESSAGES[m_hash].commit(leader_node=leader_node, sequence_number=sequence_number, m_hash=m_hash,
                                sender_node=sender_node)
        if not MESSAGES[m_hash].commit_state and len(MESSAGES[m_hash].commit_m) >= VERIFY_LIMIT:
            MESSAGES[m_hash].commit_state = True
            # store data and update database
            if leader_node != NODE_INFO:
                store_block(MESSAGES[m_hash].m)


# some node do not receive all tx and request tx data from leader node.
def tx_consensus(tx_hash_list, leader_node):
    if tx_hash_list[0] == 'zjgsu-scie':
        return
    for tx_hash in tx_hash_list:
        data = {'tx_hash': tx_hash}
        event = construct_message(data=data, index=18)
        event.wait()
        tx_raw_data = DB_ANSWER_QUEUE.get()
        if tx_raw_data is None:
            message = tx_request_message(tx_hash)
            leader_node_ = NODE.find_node(leader_node['port'])
            NODE.send_to_node(leader_node, message)


def store_block(m):
    LOGGER.info('<block:' + m['m_hash'] + ' PBFT successfully!')
    block = BlockParse().parse(block_head_raw=m['m_data']['block_head'], tx_hash_list=m['m_data']['block_tx_hash_list'])
    block.store_in_database()


def update():
    global MESSAGES
    return MESSAGES


if __name__ == '__main__':
    print('hello world')
