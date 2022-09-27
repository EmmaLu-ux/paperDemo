import time
import os
import sys

# from parse.block_parse import BlockParse
# from tools.jsonOp import file2json


os.path.join(os.path.dirname(__file__), '../')
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
from config.config import NODE_INFO, NODE
from config.thread_config import *
from p2p.message_construct import tx_request_message

def request_tx():
    tx_hash = '6c04ffbf7c8ce3846c60aced42091c6dfeb314bdf6bc78eb14a9065f7abd36a0'
    message = tx_request_message(tx_hash)
    NODE.send_to_nodes(message)

if __name__ == '__main__':
    # request_tx()
    time.sleep(5000)
    NODE.stop()



