import json
import time
import os
import sys

os.path.join(os.path.dirname(__file__), '../')
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
from parse.block_parse import BlockParse

from tools.jsonOp import file2json
from config.config import NODE_INFO, NODE, SEQUENCE_NUMBER, MESSAGES
from config.thread_config import *
from p2p.message import Message
from p2p.message_deal import message_deal


# time.sleep(0.5)
def broadcast_test(path):
    message = file2json(path)
    # message_deal(message[0])
    message_deal(message[0])


def request_test():
    message = {'m_type': 'tx_request',
               'm_hash': '6c04ffbf7c8ce3846c60aced42091c6dfeb314bdf6bc78eb14a9065f7abd36a0',
               'i': {'ip': '127.0.0.1', 'port': 8001}}
    # message_deal(message)
    NODE.send_to_nodes(message)

def pre_prepare_test(data):
    message_deal(data)

def prepare_test(data):
    message_deal(data)

def commit_test(data):
    message_deal(data)

if __name__ == '__main__':
    tx_path = '/z_test_data/tx.json'
    block_path = '/z_test_data/block.json'
    tx_data = file2json(tx_path)
    block_data = file2json(block_path)
    broadcast_test(tx_data[0])
    pre_prepare_test(block_data[0])
    prepare_test(block_data[1])
    commit_test(block_data[2])
    # time.sleep(5)
    # NODE.stop()
