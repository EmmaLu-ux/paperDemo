#!/usr/bin/env python
# _*_ coding: utf-8 _*_
"""
# @Time : 10/21/21 8:50 PM
# @Author : Archer
# @File : blockInit.py
# @desc :
"""

import time

from config.config import BLOCK_INTERNAL_TIME, LOGGER, DB_QUEST_QUEUE, DB_ANSWER_QUEUE, DB_TH_EVENT
from contract.contract import Contract
from parse.transaction_parse import TransactionParse
from tools.jsonOp import file2json, json2file
from tools.utils import *
from database.database_message_create import construct_message


# from config.thread_config import *


class BlockHead(object):
    """
    version                          4
    prev_block_hash                  32
    merkle_root_hash                 32
    time                             4
    nBits                            4
    nonce                            4
    """

    def __init__(self, version=0, prev_block_hash='0' * 64, tx_root='0' * 64, state_root='0' * 64, nBits=0x1d00ffff,
                 nonce=0, ):
        self.version = version
        self.block_height = 0
        self.prev_block_hash = prev_block_hash
        self.tx_root = tx_root
        self.state_root = state_root
        self.timestamp = int(time.time())
        self.nBits = nBits
        self.nonce = nonce
        self.block_height = None
        self.raw_data = None

    def construct(self, version=0, prev_block_hash='0' * 64, tx_root='0' * 64, state_root='0' * 64, block_height=0,
                  timestamp=0):
        self.version = version
        self.prev_block_hash = prev_block_hash
        self.tx_root = tx_root
        self.state_root = state_root
        if timestamp == 0:
            self.timestamp = int(time.time())
        else:
            self.timestamp = timestamp
        self.block_height = block_height  # get from table
        self.raw_data = self.get_raw()
        return self

    def get_raw(self):
        raw = ''
        raw += str(encode_uint32(self.version))
        raw += str(encode_uint32(self.block_height))
        raw += format_data(self.prev_block_hash)
        raw += format_data(self.tx_root)
        raw += format_data(self.state_root)
        raw += str(encode_uint32(self.timestamp))
        return raw


class Block(object):
    """
    magic_number                     4
    block_size                       4
    block_header                     80
    tx_count                         varies
    txs                              varies
    """

    def __init__(self, magic_number=0x47535858, block_size=None, tx_count=None, coninbase=None, txs=None):
        self.magic_number = magic_number
        self.block_size = block_size
        self.tx_root = None
        self.state_root = None
        self.block_height = None
        self.block_head = None
        self.block_body = None
        self.tx_count = tx_count
        self.block_hash = None
        self.txs = []
        self.txs_raw = {}
        self.raw_data = None

    def tx_merkle_construct(self):
        childs = []
        for tx in self.txs:
            childs.append(self.txs_raw[tx.tx_hash])
        if len(childs) == 0:
            childs = ['zjgsu-scie']
        parents = []
        childs = self.check_2(childs)
        for i in range(0, len(childs), 2):
            result = double_sha256(childs[i] + childs[i + 1])
            parents.append(result)

        while len(parents) != 1:
            childs = parents
            parents = []
            childs = self.check_2(childs)
            for i in range(0, len(childs), 2):
                result = double_sha256(childs[i] + childs[i + 1])
                parents.append(result)
        self.tx_root = parents[0]

    def state_merkle_construct(self):
        childs = self.get_external_account()
        parents = []
        childs = self.check_2(childs)
        for i in range(0, len(childs), 2):
            result = double_sha256(childs[i] + childs[i + 1])
            parents.append(result)

        while len(parents) != 1:
            childs = parents
            parents = []
            childs = self.check_2(childs)
            for i in range(0, len(childs), 2):
                result = double_sha256(childs[i] + childs[i + 1])
                parents.append(result)
        self.state_root = parents[0]

    def get_external_account(self):
        event = construct_message(data=None, index=4)
        event.wait()
        result = DB_ANSWER_QUEUE.get()
        user_info = [user[0] + user[1] + user[2] for user in result]
        return user_info

    def check_2(self, txs):
        """
        :param txs:
        :return:
        """
        len_txs = len(txs)
        if len_txs % 2 == 1:
            txs.append(txs[len_txs - 1])
        return txs

    def construct(self):
        self.tx_select()
        self.tx_merkle_construct()
        self.state_merkle_construct()

        event = construct_message(data=None, index=7)
        event.wait()
        pre_block = DB_ANSWER_QUEUE.get()
        # pre_block = DBOperation(None, 7)
        self.block_height = pre_block['block_height'] + 1

        self.block_head = BlockHead().construct(tx_root=self.tx_root,
                                                state_root=self.state_root,
                                                prev_block_hash=pre_block['block_hash'],
                                                block_height=self.block_height)

        self.block_hash = double_sha256(self.block_head.raw_data)
        self.block_height = self.block_head.block_height
        self.block_body = ''.join([self.txs_raw[tx.tx_hash] for tx in self.txs])

        if len(self.block_body) == 0:
            description = 'zjgsu-scie'
            self.block_body = description
        self.raw_data = self.get_raw()
        return self

    def store_in_database(self):
        data = {'block_height': self.block_height,
                'block_hash': self.block_hash,
                'block_magic_number': '58585347',
                'block_size': self.block_size,
                'block_head': self.block_head.raw_data,
                'block_body': self.block_body}
        event = construct_message(data=data, index=6)
        event.wait()
        DB_ANSWER_QUEUE.get()
        # DBOperation(data, 6)

    def get_raw(self):
        raw = ''
        raw += self.block_head.raw_data
        raw += self.block_body
        self.block_size = len(raw)
        raw = '58585347' + encode_varint(self.block_size) + raw
        return raw

    def tx_select(self):
        max_len = 1024 * 1024 - 250
        # get a unpacked tx
        len_txs = 0
        while len_txs < max_len:
            event = construct_message(data=None, index=8)
            event.wait()
            tx_raw = DB_ANSWER_QUEUE.get()

            # tx_raw = DBOperation(None, 8)
            if tx_raw is None:
                break
            tx = TransactionParse().parse(tx_raw['tx_raw_data'])
            if not tx.signature_verify():
                m = tx.tx_hash + ' verify failed!'
                LOGGER.error(m)
                return False
            self.txs.append(tx)
            self.txs_raw[tx_raw['tx_hash']] = tx_raw['tx_raw_data']
            # set tx pack state to -1 ?
            if tx.version == 1:  # trade not use
                self.update_user_info(tx)
            elif tx.version == 2:
                self.create_contract(tx)
            elif tx.version == 3:
                self.invoke_contact(tx)
            data = tx_raw

            event = construct_message(data=data, index=9)
            event.wait()
            DB_ANSWER_QUEUE.get()

            # DBOperation(tx_raw, 9)

    def update_user_info(self, tx):
        tx_info = {'from_': tx.from_,
                   'value': tx.value,
                   'to': tx.to,
                   'nonce': tx.nonce}
        data = {'pk': tx_info['from_']}

        event = construct_message(data=data, index=13)
        event.wait()
        user_from = DB_ANSWER_QUEUE.get()

        # user_from = DBOperation(data, 13)
        data = {'pk': tx_info['to']}

        event = construct_message(data=data, index=6)
        event.wait()
        user_to = DB_ANSWER_QUEUE.get()
        # user_to = DBOperation(data, 13)

        user_from['value'] -= tx_info['value']
        user_from['nonce'] += 1
        user_to['value'] += tx_info['value']

        event = construct_message(data=user_to, index=14)
        event.wait()
        result = DB_ANSWER_QUEUE.get()

        event = construct_message(data=user_from, index=14)
        event.wait()
        result = DB_ANSWER_QUEUE.get()

        # DBOperation(user_from, 14)
        # DBOperation(user_to, 14)

    def create_contract(self, tx):
        tx_info = {'from_': tx.from_,
                   'value': tx.value,
                   'to': tx.to,
                   'data': tx.data,
                   'nonce': tx.nonce}

        data = {'pk': tx_info['from_']}

        event = construct_message(data=data, index=13)
        event.wait()
        user_from = DB_ANSWER_QUEUE.get()

        # user_from = DBOperation(data, 13)
        user_from['nonce'] += 1
        # update user_info
        event = construct_message(data=user_from, index=14)
        event.wait()
        result = DB_ANSWER_QUEUE.get()

        # DBOperation(user_from, 14)
        # creat contract addr
        addr = double_sha256(tx.from_ + tx.data['hash_code'])
        data = {
            'addr': addr,
            'owner': tx.from_,
            'enc_fund': 0,
            'hash_code': tx.data['hash_code']
        }

        event = construct_message(data=data, index=10)
        event.wait()
        result = DB_ANSWER_QUEUE.get()

        # DBOperation(data, 10)
        m = 'the contract ' + tx.tx_hash + 'create successfully!'
        LOGGER.info(m)
        return tx

    def store_in_json_file(self):
        file_name = '/p2p/tx.json'
        # testdata = file2json(file_name)
        testdata = {}
        print(testdata)
        block_data = {'block_height': self.block_height,
                      'block_size': self.block_size,
                      'block_head': self.block_head.raw_data,
                      'tx_hash_list': [tx.tx_hash for tx in self.txs]}
        data = {'m_type': 'block',
                'm_owner': None,
                'm_file': None,
                'm_hash': self.block_hash,
                'm_data': block_data}
        testdata['data'] = data
        print(testdata)
        json2file(data=testdata, relative_path=file_name)

    def invoke_contact(self, tx):
        args_addr = tx.data['args_addr']
        file_path = '/transaction_file/revoke_contract_log/' + tx.to + '/' + args_addr + '.json'
        args_data = file2json(file_path)
        if tx.data['func_number'] == 0:
            t1 = args_data['invoke_create']['t1']
            t2 = args_data['invoke_create']['t2']
            domain_name = args_data['invoke_create']['domain_name']
            signature = args_data['invoke_create']['signature']
            con = Contract().create(t1=t1, t2=t2, domain_name=domain_name, signature=signature, contract_addr=tx.to)
            pass
        elif tx.data['func_number'] == 1:
            pk = args_data['invoke_commit']['pk']
            funds = args_data['invoke_commit']['funds']
            signature = args_data['invoke_commit']['sig']
            zkp = args_data['invoke_commit']['zkp']
            con = Contract().commit(pk=pk, funds=funds, sig=signature, zkp_args=zkp, contract_addr=tx.to)

        elif tx.data['func_number'] == 2:
            pk = args_data['invoke_reveal']['pk']
            c_r = args_data['invoke_reveal']['c_r']
            con = Contract().reveal(pk=pk, c_r_list=c_r, contract_addr=tx.to)
            pass

        elif tx.data['func_number'] == 3:
            con = Contract().finalize(contract_addr=tx.to)
        elif tx.data['func_number'] == 4:
            pk = args_data['invoke_update']['pk']
            domain_name = args_data['invoke_update']['domain_name']
            ip = args_data['invoke_update']['ip']
            sig = args_data['invoke_update']['signature']

            con = Contract().update(pk=pk, domain_name=domain_name, ip=ip, sig=sig, contract_addr=tx.to)

        elif tx.data['func_number'] == 5:
            pk1 = args_data['invoke_transfer']['pk1']
            pk2 = args_data['invoke_transfer']['pk2']
            domain_name = args_data['invoke_transfer']['domain_name']

            sig = args_data['invoke_transfer']['signature']
            funds = args_data['invoke_transfer']['funds']
            end_time = args_data['invoke_transfer']['end_time']
            con = Contract().transfer(pk1=pk1, domain_name=domain_name, pk2=pk2, sig=sig, funds=funds,end_time=end_time,
                                      contract_addr=tx.to)

        elif tx.data['func_number'] == 6:
            pk2 = args_data['invoke_receiver']['pk2']
            domain_name = args_data['invoke_receiver']['domain_name']
            funds = args_data['invoke_receiver']['funds']
            zkp = args_data['invoke_receiver']['zkp']
            con = Contract().receiver(domain_name=domain_name, pk2=pk2, funds=funds, zkp_args=zkp,contract_addr=tx.to)

        elif tx.data['func_number'] == 7:
            pk1 = args_data['invoke_renewal']['pk1']
            pk2 = args_data['invoke_renewal']['pk2']
            domain_name = args_data['invoke_renewal']['domain_name']
            funds = args_data['invoke_renewal']['funds']
            sig = args_data['invoke_renewal']['signature']
            zkp = args_data['invoke_renewal']['zkp']

            con = Contract().renewal(pk1=pk1, pk2=pk2, domain_name=domain_name, funds=funds, zkp_args=zkp, sig=sig, contract_addr=tx.to)

            pass

# if __name__ == '__main__':
#     initblock = Block().construct()
#     initblock.store_in_json_file()
