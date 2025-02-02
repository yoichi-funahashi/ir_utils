from machine import Pin
from UpyIrTx import UpyIrTx
from UpyIrRx import UpyIrRx

__T_NEC = const(562)
__T_AEHA = const(425)
__T_SONY = const(600)
NEC = const('NEC')
AEHA = const('AEHA')
SONY = const('SONY')

def __djage_format(leader1, leader2):
    # NECフォーマット
    if round(leader1 / __T_NEC) == 16 and round(leader2 / __T_NEC) == 8:
        return __T_NEC, NEC
    # 家製協(AEHA)フォーマット
    elif round(leader1 / __T_AEHA) == 8 and round(leader2 / __T_AEHA) == 4:
        return __T_AEHA, AEHA
    # SONYフォーマット
    elif round(leader1 / __T_SONY) == 4:
        return __T_SONY, SONY
    else:
        return None, None


def __get_user_data_code(data_list):
    bit_list_1 = []
    bit_list_2 = []
    bit_list_3 = []
    bit_list_4 = []
    for i in range(0, 8):
        i1 = i * 2
        i2 = i * 2 + 1
        if data_list[i1] == 1 and data_list[i2] == 1:
            bit_list_1.insert(0, '0')
        if data_list[i1] == 1 and data_list[i2] == 3:
            bit_list_1.insert(0, '1')
    for i in range(8, 16):
        i1 = i * 2
        i2 = i * 2 + 1
        if data_list[i1] == 1 and data_list[i2] == 1:
            bit_list_2.insert(0, '0')
        if data_list[i1] == 1 and data_list[i2] == 3:
            bit_list_2.insert(0, '1')
    for i in range(16, 24):
        i1 = i * 2
        i2 = i * 2 + 1
        if data_list[i1] == 1 and data_list[i2] == 1:
            bit_list_3.insert(0, '0')
        if data_list[i1] == 1 and data_list[i2] == 3:
            bit_list_3.insert(0, '1')
    for i in range(24, 32):
        i1 = i * 2
        i2 = i * 2 + 1
        if data_list[i1] == 1 and data_list[i2] == 1:
            bit_list_4.insert(0, '0')
        if data_list[i1] == 1 and data_list[i2] == 3:
            bit_list_4.insert(0, '1')

    return f'{int('0b'+''.join(bit_list_1), 0):02x}' + f'{int('0b'+''.join(bit_list_2), 0):02x}', f'{int('0b'+''.join(bit_list_3), 0):02x}' + f'{int('0b'+''.join(bit_list_4), 0):02x}'


def ir_read(pin=14, wait_ms=3000, blank_ms=200, stop_size=1023, rx_size=1023, rx_idle_level=1):
    rx_pin = Pin(pin, Pin.IN)
    rx = UpyIrRx(rx_pin, rx_size, rx_idle_level)
    signal_list = []
    if rx.record(wait_ms=wait_ms, blank_ms=blank_ms, stop_size=stop_size) == UpyIrRx.ERROR_NONE:
        signal_list = rx.get_calibrate_list()
        if len(signal_list) < 2:
            return {'result': 'NG', 'ir_type': None, 'user_code': None, 'data_code': None, 'read_data': None, 'org_read_data': None}
        t, ir_type = __djage_format(signal_list[0], signal_list[1])
        if ir_type is None:
            return {'result': 'NG', 'ir_type': None, 'user_code': None, 'data_code': None, 'read_data': None, 'org_read_data': None}
        data_list = [round(val / t) for val in signal_list]
        user_code = None
        data_code = None
        if ir_type == NEC:
            ir_data_list = data_list[2:66]
            user_code, data_code = __get_user_data_code(ir_data_list)
        if ir_type == AEHA:
            # TODO 未実装
            pass
        if ir_type == SONY:
            # TODO 未実装
            pass
        return {'result': 'OK', 'ir_type': ir_type, 'user_code': user_code, 'data_code': data_code, 'read_data': [val * t for val in data_list], 'org_read_data': signal_list}
    else:
        return {'result': 'NG', 'ir_type': None, 'user_code': None, 'data_code': None, 'read_data': None, 'org_read_data': None}


def ir_send(ch=0, pin=15, ir_type=None, user_code=None, data_code=None, ir_data=None, tx_freq=38000, tx_duty=30, tx_idle_level=0):
    
    tx_pin = Pin(pin, Pin.OUT)
    tx = UpyIrTx(ch, tx_pin, tx_freq, tx_duty, tx_idle_level)

    if user_code is not None and data_code is not None:
        
        bit_data = list(reversed(list(f'{int('0x' + user_code[0:2], 0):08b}')))
        bit_data += list(reversed(list(f'{int('0x' + user_code[2:4], 0):08b}')))
        bit_data += list(reversed(list(f'{int('0x' + data_code[0:2], 0):08b}')))
        bit_data += list(reversed(list(f'{int('0x' + data_code[2:4], 0):08b}')))
    #    print(bit_data)

        t = 0
        # NECフォーマット
        if ir_type == NEC:
            t = __T_NEC
            ir_data = [16 * t, 8 * t, ]
            for b in bit_data:
                if b == '0':
                    ir_data.append(t)
                    ir_data.append(t)
                if b == '1':
                    ir_data.append(t)
                    ir_data.append(t * 3)
            ir_data.append(1 * t)
            ir_data.append(170 * t)
            ir_data.append(16 * t)
            ir_data.append(4 * t)
            ir_data.append(1 * t)

        # 家製協(AEHA)フォーマット
        elif ir_type == AEHA:
            t = __T_AEHA
            # TODO データ作成部分の実装が必要
            ir_data = [8 * t, 4 * t, ]
            for b in bit_data:
                if b == '0':
                    ir_data.append(t)
                    ir_data.append(t)
                if b == '1':
                    ir_data.append(t)
                    ir_data.append(t * 3)
            return 'NG', None

        # SONYフォーマット
        elif ir_type == SONY:
            t = __T_SONY
            # TODO データ作成部分の実装が必要
            ir_data = [4 * t, ]
            return 'NG', None
        
        else:
            return 'NG', None
    
    else:
        if ir_data is None:
            return 'NG', None
    
    try:
        if tx.send(ir_data):
            return 'OK', ir_data
        else:
            return 'NG', ir_data
    except:
        return 'NG', None

