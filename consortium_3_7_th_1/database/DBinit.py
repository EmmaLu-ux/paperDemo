import pymysql
import sys
sys.path.append('../')
from tools.jsonOp import file2json


from tools.ecdsa_signature import genetor_keys
from tools.utils import double_sha256
from tools.print_format import *
from tools.pointsMul import *
from config.config import ecc_table
import time
import datetime


mydb = pymysql.connect(
    host="localhost",
    user="root",
    passwd="abc123",
    database="consortium_1",
)

mydb.rollback()
mycursor = mydb.cursor()


def table_init():
    print_success('\n==============================================')
    sql = "DROP TABLE IF exists block"
    mycursor.execute(sql)
    sql = """CREATE TABLE block (id INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
                                  block_height INT(11) NOT NULL,
                                  block_hash CHAR(64) NOT NULL,
                                  block_magic_number CHAR(8) NOT NULL,
                                  block_size CHAR(20) NOT NULL,
                                  block_head TEXT NOT NULL,
                                  block_body TEXT NOT NULL,
                                  PRIMARY KEY (id))"""
    mycursor.execute(sql)
    print_success('block table create successfully!')

    sql = "DROP TABLE IF exists transaction"
    mycursor.execute(sql)
    sql = """CREATE TABLE transaction (id INT UNSIGNED NOT NULL AUTO_INCREMENT,
                                        tx_version CHAR(10) NOT NULL,
                                        tx_hash  CHAR(80) NOT NULL,
                                        tx_from CHAR(128) NOT NULL,
                                        tx_to CHAR(128) NOT NULL,
                                        tx_value CHAR(32) NOT NULL,
                                        tx_data TEXT NOT NULL,
                                        tx_signature CHAR(255) NOT NULL,
                                        nonce CHAR(10) NOT NULL,
                                        if_pack CHAR(5) NOT NULL,   
                                        PRIMARY KEY (id))"""
    mycursor.execute(sql)
    print_success('transaction table create successfully!')

    sql = "DROP TABLE IF exists transaction_raw"
    mycursor.execute(sql)
    sql = """CREATE TABLE transaction_raw (id INT UNSIGNED NOT NULL AUTO_INCREMENT,
                                           tx_hash  CHAR(80) NOT NULL,
                                           raw_data TEXT NOT NULL,
                                           if_pack CHAR(5) NOT NULL,   
                                           PRIMARY KEY (id))"""
    mycursor.execute(sql)
    print_success('transaction_raw table create successfully!')

    sql = "DROP TABLE IF exists external_account"
    mycursor.execute(sql)
    sql = """CREATE TABLE external_account(id INT UNSIGNED NOT NULL AUTO_INCREMENT,
                                        username CHAR(50) NOT NULL,
                                        password CHAR(50) NOT NULL,
                                        pk CHAR(128) NOT NULL,
                                        sk CHAR(128) NOT NULL,
                                        token CHAR(10) NOT NULL,
                                        enc_fund CHAR(255) NOT NULL,
                                        nonce CHAR(10) NOT NULL,
                                        change_height CHAR(255) NOT NULL,
                                        PRIMARY KEY (id))"""
    mycursor.execute(sql)
    print_success('external_account table create successfully!')

    sql = "DROP TABLE IF exists contract_account"
    mycursor.execute(sql)
    sql = """CREATE TABLE contract_account(id INT UNSIGNED NOT NULL AUTO_INCREMENT,
                                        addr  CHAR(64) NOT NULL,
                                        owner CHAR(128) NOT NULL,
                                        enc_fund CHAR(255) NOT NULL,
                                        hash_code CHAR(64) NOT NULL,
                                        PRIMARY KEY (id))"""
    mycursor.execute(sql)
    print_success('contract_account table create successfully!')

    sql = "DROP TABLE IF exists domain_account"
    mycursor.execute(sql)
    sql = """CREATE TABLE domain_account(id INT UNSIGNED NOT NULL AUTO_INCREMENT,
                                        domain_name CHAR(100) NOT NULL,
                                        addr  CHAR(80) NOT NULL,
                                        ip CHAR(20) NOT NULL,
                                        expiration_date CHAR(20) NOT NULL,
                                        owner CHAR(255) NOT NULL,
                                        state CHAR(10) NOT NULL,
                                        PRIMARY KEY (id))"""
    mycursor.execute(sql)
    print_success('domain_account table create successfully!')

    sql = "DROP TABLE IF exists node"
    mycursor.execute(sql)
    sql = """CREATE TABLE node(id INT UNSIGNED NOT NULL AUTO_INCREMENT,
                                ip  CHAR(20) NOT NULL,
                                port CHAR(8) NOT NULL,
                                sk    CHAR(64) NOT NULL, 
                                pk    CHAR(128) NOT NULL,
                                PRIMARY KEY (id))"""
    mycursor.execute(sql)
    print_success('node table create successfully!')
    mydb.commit()
    print_success('==============================================\n')


def data_init():
    print_success('\n==============================================')
    users = ['root', 'mike', 'alice', 'bob', 'archer']
    password = ['abc123', 'abc123', 'abc123', 'abc123', 'abc123', ]
    pk = [
        '211cc8124628d2595574193e3d72a94ba911350e87915c7b51946d3706223f2e03c55c43ffd727359e19c719cc9b314a634a967a095e0b36de969bfe68bd4749',
        '8aefabbd333f1ad425e8a196f851d8c9a4b85b969b3d4a3daadb4f5f01d06e50e925474cae3e40172f31700507efa3400079048448f65b6afe780096669462f9',
        'daf7575bd9d6a3453383b0e633a967c99c63123d21cd91162af918539275d6da251f5c5c35094bf6c3c81f674ced3c231f294d479eed49037e4bbd90022566c2',
        '8c565582bc41fb15e3009bb7bd8454e752f7e136eec4458fb8d80edf31298b517c3aa39e66709cfe7a9236040edabe5380f3a9f77eb3d01a14120ad5a829eed2',
        'b9db5af0b4d9dd98b01f6b56de2596aef09409ea693d913230cbdb7847029583a7f0c0dd6b0adca6f9b943d4bb5d6982e94e323f5f501f06ad4fea0fcdd12ac4']
    sk = ['cde64df81686633ebb99ec6a70731bee0fc268759b4ea46af0f76b386f960b1d',
          '4ecf28782f79ce0124e311fd458289640e221b097dcfea68251ebd796bad7b37',
          '55cd4ad75cbe5c0ba867e359931ba5418e1763c6c0c7890a8724735ac64f1300',
          '62d314a3ef0a2fa8668a2e6742a4cbb418b9c25ae44307b5dd3fb9f68fff9949',
          'f008824cf29d38757fc22748f77e8a74aeb12afd11cc590a0138242aa9acd66f']
    r = [5, 1000, 1000, 1000, 1000]
    g = strToPoints(ecc_table['g'])
    h = strToPoints(ecc_table['h'])
    g_100 = scalar_mult(100, g)
    for i in range(0, 5):
        # sk, pk = genetor_keys()
        h_r = scalar_mult(r[i], h)
        enc_fund = point_add(g_100, h_r)
        sql = " INSERT INTO  external_account(username, password, pk, sk, token, enc_fund, nonce, change_height) VALUES ('%s', '%s', '%s', '%s', '%s','%s','%s','%s')" % (
            users[i], password[i], pk[i], sk[i], '100', pointsToStr(enc_fund), '0', '0')
        mycursor.execute(sql)
    print_success('external_account table data init successfully!')

    for i in range(0, 100):
        domain_name = 'http://test' + str(i) +'.com'
        ip = '127.0.0.1:8013'
        addr = double_sha256(domain_name)
        expiration_date = int(
            time.mktime(datetime.date(datetime.date.today().year, (datetime.date.today().month) % 12 + 1, 1).timetuple()))
        sql = " INSERT INTO  domain_account(domain_name, addr, ip, expiration_date, owner, state) VALUES ('%s', '%s', '%s', '%s','%s','%s')" % (
            domain_name, addr, ip, expiration_date, pk[0], '0')
        mycursor.execute(sql)
        mydb.commit()
        print_success('domain_account table data init successfully!')

    for i in range(0, 5):
        sk, pk = genetor_keys()
        sql = " INSERT INTO  node(ip, port, sk, pk) VALUES ('%s', '%s', '%s', '%s')" % (
            '127.0.0.1', str(8001 + i), sk, pk)
        mycursor.execute(sql)
    print_success('node table data init successfully!')
    print_success('==============================================\n')
    mydb.commit()

    data = {
        'block_height': 0,
        'block_hash': 'fcf8579763e3c3dff4fdf8196eea5fda8572c8e0d22c2df5e60d90ac15fc9b73',
        'block_magic_number': '58585347',
        'block_size': '233',
        'block_head': '0000000000000000000000000000000000000000000000000000000000000000000000000000000056510933f0878820defaaf25a6127a964da4250b005eaf5ca35795cba9ab48363ade9a2dc7543ceb1fe8a4b69b9001297692ad31ccdb10adaf5606d93e6907b510db9461',
        'block_body': 'zjgsu-scie-archer',
    }
    sql = "insert into block(block_height, block_hash, block_magic_number, block_size, block_head, block_body) values ('%d', '%s', '%s', '%s', '%s', '%s')" % (
        data['block_height'], data['block_hash'], data['block_magic_number'], data['block_size'],
        data['block_head'],
        data['block_body'])
    mycursor.execute(sql)
    print_success('block 0 has been stored successfully!')
    print_success('==============================================\n')
    mydb.commit()

def contract_init():
    file_path = '/z_test_data/contract.json'
    contract_list = file2json(file_path)
    data = {'owner': '211cc8124628d2595574193e3d72a94ba911350e87915c7b51946d3706223f2e03c55c43ffd727359e19c719cc9b314a634a967a095e0b36de969bfe68bd4749',
            'enc_fund': '0',
            'hash_code': 'abcd'}

    for c in contract_list:
        data['addr'] = c
        sql = "INSERT INTO contract_account(addr, owner, enc_fund, hash_code) VALUES ('%s','%s','%s','%s')" % (
            data['addr'], data['owner'], data['enc_fund'], data['hash_code'])
        mycursor.execute(sql)
        mydb.commit()
    print_success('contract init successfully!')

if __name__ == '__main__':
    table_init()
    data_init()
    contract_init()
    mydb.close()
    exit(0)

