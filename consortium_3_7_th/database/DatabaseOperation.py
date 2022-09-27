# !/usr/bin/env python
# -*- coding: utf-8
from config.config import *
from tools.print_format import *


def th_DBOperation():
    global DB_QUEST_QUEUE, DB_ANSWER_QUEUE
    while True:
        if DB_QUEST_QUEUE.empty():
            DB_TH_EVENT.clear()
            DB_TH_EVENT.wait()
        message = DB_QUEST_QUEUE.get()
        data = message[0]
        choice = message[1]
        event = message[2]
        result = DBOperation(data, choice)
        DB_ANSWER_QUEUE.put(result)
        event.set()


def DBOperation(data=None, choice=None):
    result = None
    if choice == 1:
        sql = "select * from external_account where username = '%s' AND password = '%s'" % (
            data['username'], data['password'])
        mycursor.execute(sql)
        result = mycursor.fetchone()
        if result is not None:
            result = get_dict(result, 1)
    elif choice == 2:
        sql = "insert into transaction(tx_hash, tx_version, tx_from, tx_to, tx_value, tx_data, tx_signature, nonce,if_pack) values ('%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (
            data['tx_hash'], data['tx_version'], data['tx_from'], data['tx_to'], data['tx_value'], data['tx_data'], data['tx_signature'],
            data['tx_nonce'], data['if_pack'])
        mycursor.execute(sql)
        mydb.commit()
    elif choice == 3:
        sql = "insert into transaction_raw(tx_hash, raw_data, if_pack) values ('%s', '%s', '%s')" % (
            data['tx_hash'], data['raw_data'], data['if_pack'],)
        mycursor.execute(sql)
        mydb.commit()
    elif choice == 4:
        sql = "SELECT pk, enc_fund, change_height FROM external_account"
        mycursor.execute(sql)
        result = mycursor.fetchall()
        # result = get_dict(result, 4)
    elif choice == 5:
        sql = "UPDATA external_account SET token=%s, enc_fund=%s, nonce=%s, change_height=%s WHERE pk='%s" % (
            data['token'], 'aaaaaaaa', data['nonce'], data['change_height'], data['pk'])
        mycursor.execute(sql)
    elif choice == 6:
        sql = "insert into block(block_height, block_hash, block_magic_number, block_size, block_head, block_body) values ('%d', '%s', '%s', '%s', '%s', '%s')" % (
            data['block_height'], data['block_hash'], data['block_magic_number'], data['block_size'],
            data['block_head'],
            data['block_body'])
        mycursor.execute(sql)
        mydb.commit()
        s = '<block_height: ' + str(data['block_height']) + ', block_hash:' + data[
            'block_hash'] + ' store successfully!>'
        print_success(s)
    elif choice == 7:
        sql = "select block_height, block_hash, block_head From block where block_height = (select max(block_height) from block)"
        mycursor.execute(sql)
        result = mycursor.fetchone()
        result = get_dict(result, 7)
    elif choice == 8:
        sql = "SELECT tx_hash,raw_data FROM transaction_raw WHERE id = (SELECT min(id) FROM transaction_raw WHERE if_pack = '0')"
        mycursor.execute(sql)
        result = mycursor.fetchone()
        if result is not None:
            result = get_dict(result, 8)
    elif choice == 9:
        sql = "UPDATE transaction SET if_pack = '1' WHERE tx_hash='%s'" % data['tx_hash']
        mycursor.execute(sql)
        sql = "UPDATE transaction_raw SET if_pack = '1' WHERE tx_hash='%s'" % data['tx_hash']
        mycursor.execute(sql)
        mydb.commit()
    elif choice == 10:
        sql = "INSERT INTO contract_account(addr, owner, enc_fund, hash_code) VALUES ('%s','%s','%s','%s')" % (
        data['addr'], data['owner'], data['enc_fund'], data['hash_code'])
        mycursor.execute(sql)
        mydb.commit()
    elif choice == 11:
        sql = "SELECT * FROM domain_account WHERE domain_name = '%s'" % (data['domain_name'])
        mycursor.execute(sql)
        result = mycursor.fetchone()
        result = get_dict(result, 11)
    elif choice == 12:
        sql = "UPDATE domain_account SET state = %s WHERE domain_name='%s'" % (data['domain_state'], data['domain_name'])
        mycursor.execute(sql)
        mydb.commit()
    elif choice == 13:
        # sql = "SELECT pk, token, nonce, enc_fund FROM external_account where pk = '%s'" % data['pk']
        sql = "SELECT pk, token, nonce, enc_fund FROM external_account where pk = '%s'" % data['pk']
        mycursor.execute(sql)
        result = mycursor.fetchone()
        result = get_dict(result, 13)
        mydb.commit()
    elif choice == 14:
        sql = "UPDATE external_account SET token = '%s', nonce = '%s' WHERE pk = '%s'" %(data['value'], data['nonce'], data['pk'])
        mycursor.execute(sql)
        mydb.commit()
    elif choice == 15:
        sql = "UPDATE domain_account SET state='0' ,owner = '%s' WHERE domain_name = '%s'" % (data['user_pk'], data['domain_name'])
        mycursor.execute(sql)
        mydb.commit()
    elif choice == 16:
        sql = "UPDATE domain_account SET state='1' WHERE domain_name = '%s' " % (data['domain_name'])
        mycursor.execute(sql)
        mydb.commit()
    elif choice == 17:
        sql = "SELECT token FROM external_account WHERE pk = '%s'" % (data['pk'])
        mycursor.execute(sql)
        token = int(mycursor.fetchone()[0]) - PUNISH_FEE
        sql = "UPDATE external_account SET token = '%s'WHERE pk = '%s' " % (token, data['pk'])
        mycursor.execute(sql)
    elif choice == 18:
        sql = "SELECT raw_data FROM transaction_raw WHERE tx_hash = '%s'" % (data['tx_hash'])
        mycursor.execute(sql)
        sql_result = mycursor.fetchone()
        if sql_result is not None:
            result = sql_result[0]
    elif choice == 19:
        sql = "UPDATE domain_account SET ip = '%s' WHERE domain_name = '%s'" % (data['ip'], data['domain_name'])
        mycursor.execute(sql)
        mydb.commit()
    elif choice == 20:
        sql = "SELECT raw_data FROM transaction_raw WHERE tx_hash = '%s'" % (data['tx_hash'])
        mycursor.execute(sql)
        result = mycursor.fetchone()
        if result is not None:
            result = True
        else:
            result = False
    elif choice == 21:
        sql = "SELECT enc_fund FROM contract_account where  addr = '%s'" % (data['addr'])
        mycursor.execute(sql)
        result = mycursor.fetchone()[0]
    elif choice == 22:
        sql = "UPDATE external_account SET enc_fund = '%s' WHERE pk = '%s'" % (data['enc_fund'], data['user_pk'])
        mycursor.execute(sql)
        mydb.commit()
    elif choice == 23:
        sql = "UPDATE contract_account SET enc_fund = '%s' WHERE addr = '%s'" % (data['enc_fund'], data['contract_addr'])
        mycursor.execute(sql)
        mydb.commit()
    elif choice == 24:
        sql = "UPDATE domain_account SET expiration_date = '%s' WHERE domain_name = '%s'" % (data['expiration'], data['domain_name'])
        mycursor.execute(sql)
        mydb.commit()
    return result


def get_dict(result, choice):
    if choice == 1:
        data = {'username': result[1],
                'password': result[2],
                'pk': result[3],
                'sk': result[4],
                'token': result[5],
                'enc_fund': result[6],
                'nonce': result[7],
                'change_height': result[8]}
    elif choice == 5:
        data = {'tx_hash': result[1],
                'tx_output_index': result[2],
                'tx_value': int(result[3])}
    elif choice == 7:
        data = {
            'block_height': result[0],
            'block_hash': result[1],
            'block_head': result[2]}
    elif choice == 8:
        data = {'tx_hash': result[0],
                'tx_raw_data': result[1]}
    elif choice == 11:
        data = {'domain_name': result[1],
                'addr': result[2],
                'ip': result[3],
                'expiration': result[4],
                'owner': result[5],
                'state': result[6]
                }
    elif choice == 13:
        data = {'pk': result[0],
                'value': int(result[1]),
                'nonce': int(result[2]),
                'enc_fund': result[3],
                }
    return data


if __name__ == '__main__':
    pass
    # data = {'username': 'archer'}
    # print DBOperation(data, 13)
    # storeDB(None, 16)
