import queue
import threading
import time

import pymysql.connections
import os
from log.log import init_log


BLOCK_INTERNAL_TIME = 5
from tools.pointsMul import strToPoints

COST_TIME_PATH = '/z_test_data/cost_time.json'
TEST_KEY = 'commit'
DEMO_AMOUNT = 5
ecc_table = {
    'n': 'FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141',
    'p': 'FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFC2F',
    'g': '79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798'
         '483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8',
    'a': '0000000000000000000000000000000000000000000000000000000000000000',
    'b': '0000000000000000000000000000000000000000000000000000000000000007',
    'p': '0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f',
    'h': '600998e827cc894580d3b0c17d6e9f53976d44c876b17888cdaf08bf6ff91db90'
         '4e7b10295b6d328f4bf1bd0aacf9e6f471b93bbc36e9382a9a0824bd7c09c17'
}  # secp256k1


mydb = pymysql.connect(
    host="127.0.0.1",
    user="root",
    passwd="abc123",
    database="consortium",
)

mydb.rollback()
mycursor = mydb.cursor()

L_MAX = 10
FUND_G = strToPoints(ecc_table['g'])
FUND_H = strToPoints(ecc_table['h'])

config_path = os.getcwd()[:]
COMMON_PATH = config_path[:config_path.rfind('/')]


DB_QUEST_QUEUE = queue.Queue(1000)
DB_ANSWER_QUEUE = queue.Queue(1000)
DB_TH_EVENT = threading.Event()

MESSAGE_QUEUE = queue.Queue(1000)
MESSAGE_TH_EVENT = threading.Event()

PUNISH_FEE = 10
LOGGER = init_log()



NODE_INFO = {'ip': '127.0.0.1',
             'port': 8001}

NODE_LIST = [{'ip': '127.0.0.1',
              'port': 8001},
             {'ip': '127.0.0.1',
              'port': 8002},
             {'ip': '127.0.0.1',
              'port': 8003},
             {'ip': '127.0.0.1',
              'port': 8004},
             {'ip': '127.0.0.1',
              'port': 8005}]


from p2p.node import Node
NODE = Node(NODE_INFO['ip'], NODE_INFO['port'])
NODE.start()
#
time.sleep(0.5)
NODE.connect_with_node('127.0.0.1', 8002)
time.sleep(0.1)
NODE.connect_with_node('127.0.0.1', 8003)
time.sleep(0.1)
NODE.connect_with_node('127.0.0.1', 8004)
time.sleep(0.1)
NODE.connect_with_node('127.0.0.1', 8005)
input('start')
NODE_NUMBER = len(NODE_LIST)
VERIFY_LIMIT = 2

MESSAGES = {}

SEQUENCE_NUMBER = 0

