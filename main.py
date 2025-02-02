from machine import Pin
import ir_utils
import time

__LED_PIN = const(25)
led = Pin(__LED_PIN, Pin.OUT)
saved_result = None

time.sleep(3)
while True:
    
    # --------------------
    # 赤外線リモコン 読み込み
    # --------------------
    led.value(1)
    print('read start')
    
    result = ir_utils.ir_read(pin=14, wait_ms=5000)

    print(f'Format: {result["ir_type"]}')
    print(f'UserCode: {result["user_code"]}')
    print(f'DataCode: {result["data_code"]}')
    print(f'IR DATA: {str(result["read_data"])}')
    print(f'ORIGINAL DATA: {str(result["org_read_data"])}')

    led.value(0)
    print('read end\n')
    time.sleep(5)
    
    if result['result'] == 'OK':
        saved_result = result
        
    # --------------------
    # 赤外線リモコン 送信
    # --------------------
    led.value(1)
    print('send start')

    if saved_result is None:
        print('not send')
    else:
        if saved_result['ir_type'] is not None and saved_result['user_code'] is not None and saved_result['data_code'] is not None:
            result, send_ir_data = ir_utils.ir_send(ir_type=saved_result['ir_type'], user_code=saved_result['user_code'], data_code=saved_result['data_code'])
            print('send by user_code and data_code ' + result)
            print(f'IR DATA: {str(send_ir_data)}')
        elif saved_result['read_data'] is not None:
            result, send_ir_data = ir_utils.ir_send(ir_data=saved_result['read_data'])
            print('send by ir_data ' + result)
            print(f'IR DATA: {str(send_ir_data)}')
        else:
            print('not send')

    led.value(0)
    print('send end\n')
    time.sleep(5)
