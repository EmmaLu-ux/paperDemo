# coding=utf-8
import hashlib
import struct
import sys
from binascii import hexlify  # 二进制转换成十六进制

if sys.version > '3':
    to_int = lambda x: int(x, 16)
else:
    to_int = ord


def format_data(data):
    return ''.join([data[i-2:i] for i in range(len(data), 0, -2)])


def format_hash(data):
    return ''.join([data[i-2:i] for i in range(len(data), 0, -2)])

def encode_uint16(data):
    data = int(data)
    data = hex(data)[2:].zfill(4)
    return bytes.fromhex(data)[::-1].hex()

def decode_uint16(data):
    """将原来小端序字符型的数据转换成正常的数字
    :param data:
    :return:
    """
    assert (len(data) == 4)
    return int(bytes.fromhex(data)[::-1].hex(), 16)


def encode_uint32(data):
    # assert (len(data) == 4)
    data = int(data)
    data = hex(data)[2:].zfill(8)
    return bytes.fromhex(data)[::-1].hex()


def decode_uint32(data):
    assert (len(data) == 8)
    return int(bytes.fromhex(data)[::-1].hex(), 16)


def encode_uint64(data):
    # assert (len(data) == 8)
    data = int(data)
    data = hex(data)[2:].zfill(16)
    return bytes.fromhex(data)[::-1].hex()


def decode_uint64(data):
    assert (len(data) == 16)
    return int(bytes.fromhex(data)[::-1].hex(), 16)


def encode_varint(data):
    """
        大小                     例子                   描述
        <=0xff                   0x12                  占用一个字节
        <=0xffff                 0xfd1234              前缀为fd，小端表示接下来的两个字节
        <=0xffffffff             0xfe12345678          前缀为fe，小端表示接下来的四个字节
        <= 0xffffffffffffffff    0xff1234567890abcdef  前缀为ff，小端表示接下来的八个字节
    """

    result = 0
    format_ = None
    assert (data >= 0)
    if data <= 0xff:
        data = hex(data)[2:]
        if len(data) % 2 == 1:
            data = '0' + data
        result = data
    elif data <= 0xffff:
        format_ = "<H"
        prefix = 0xfd
        result = hex(prefix)[2:] + bytes.fromhex(hex(data)[2:].zfill(4))[::-1].hex()
    elif data <= 0xffffffff:
        format_ = "<I"
        prefix = 0xfe
        result = hex(prefix)[2:] + bytes.fromhex(hex(data)[2:].zfill(8))[::-1].hex()
    elif data <= 0xffffffffffffffff:
        format_ = "<Q"
        prefix = 0xff
        result = hex(prefix)[2:] + bytes.fromhex(hex(data)[2:].zfill(16))[::-1].hex()
    return result







def decode_varint(data):
    """
    大小                     例子                   描述
    <=0xfc                   0x12                  占用一个字节
    <=0xffff                 0xfd1234              前缀为fd，小端表示接下来的两个字节
    <=0xffffffff             0xfe12345678          前缀为fe，小端表示接下来的四个字节    
    <= 0xffffffffffffffff    0xff1234567890abcdef  前缀为ff，小端表示接下来的八个字节    
    """

    assert (len(data) > 0)
    size = to_int(data[:2])
    assert (size <= 255)

    if size < 253:
        return size, 2


    if size == 253:
        size_ = 4
    elif size == 254:
        size_ = 8
    elif size == 255:
        size_ = 16
    else:
        assert 0, 'unknow format_ for size: {size}'.format(size=size)

    size = int(bytes.fromhex(data[2:size_+2])[::-1].hex(), 16)
    return size, size_ + 2


def is_public_key(hex_data):
    if type(hex_data) != bytes:
        return False

    if len(hex_data) == 65 and to_int(hex_data[0]) == 4:
        return True

    if len(hex_data) == 33 and to_int(hex_data[0]) in (2, 3):
        return True


def double_sha256(data):
    # for convenience, we decide use sha256 instead of double sha256
    # return hashlib.sha256(hashlib.sha256(data.encode()).digest()).hexdigest()
    return hashlib.sha256(data.encode()).hexdigest()


def sha256(data):
    return hashlib.sha256(data.encode()).hexdigest()

def hash160(data):
    hash_256_value = hashlib.sha256(data.encode()).hexdigest()
    obj = hashlib.new('ripemd160', hash_256_value.encode('utf-8'))
    ripemd_160_value = obj.hexdigest()
    return ripemd_160_value

