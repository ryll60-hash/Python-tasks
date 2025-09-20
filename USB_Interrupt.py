import socket
import serial
import time
import json
import random

def parse_json(json_string):
    try:
        return json.loads(json_string)
    except json.JSONDecodeError:
        return "Invalid JSON"
    

def calculate_lrc(message):
    lrc = 0
    for byte in message:
        lrc ^= byte
    return lrc


def send_message_with_lrc(port, message):
    ser = serial.Serial(
        port,
        baudrate=9600,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=1
    )

    message_with_header = bytearray([0x02, 0x66, 0x01])
    message_length = len(message).to_bytes(2, byteorder='big')
    message_with_header.extend(message_length)
    message_with_header.extend(message)
    lrc = calculate_lrc(message)
    message_with_header.append(lrc)

    ser.write(message_with_header)

    response = bytearray()
    start_time = time.time()
    timeout = 2  # seconds

    while True:
        if ser.in_waiting:
            response.extend(ser.read(ser.in_waiting))
        if time.time() - start_time > timeout:
            break
        time.sleep(0.01)  # avoid busy loop

    ser.close()

    if response:
        print("Отримана відповідь від сервера:", response)
        return response
    else:
        print("⚠️ Від сервера не отримано відповіді")
        return None


# ======== Твої повідомлення =========
messagePurchase1 = b'{"method": "Purchase","step":"0","params": {"transAmount": "4720","transCurrency": "980", "merchantId": "20900448","transactionUid": "2i89y0787759"}}'
messagePurchase2 = b'{"method": "Purchase","step":"2","params": {"transAmount": "4780","transCurrency": "980", "merchantId": "20900448","transactionUid": "2i89y0787759"}}'
messageGetStatus  = b'{"method": "GetStatus"}'
messageGetLastResult = b'{"method": "GetLastResult"}'
messageInterrupt = b'{"method": "Interrupt"}'

com_port = 'COM8'

merchant_ids = ["TG001079", "0173101", "TG0010791111111","017310122222222"]
index = 0

# ======== Основний цикл =========
for i in range(8):
    transaction_uid = f"2i89y079772{i+1:01d}"
    random_amount = str(random.randint(4000, 79999))

    merchant_id = merchant_ids[index % len(merchant_ids)] #послідовна передача мерчантів
    index += 1
    
    random_merchantId = random.choice(merchant_ids)    #рендомна передача мерчантів
    purchase_dict = {"method": "Purchase", "step": "0", "params": {"transAmount": random_amount, "transCurrency": "980", "merchantId": "20900448", "transactionUid": transaction_uid }}
    messagePurchase = json.dumps(purchase_dict).encode('utf-8')
#       purchase_dict = {"method": "Echo", "params": {"merchantId": merchant_id}}
#        purchase_dict = {"method": "ZReport", "params": {"merchantId": merchant_id}}
    print(f"==== Початок циклу {i+1} ====")
    time.sleep(1)
    send_message_with_lrc(com_port, messagePurchase)
    for i in range(120):
        time.sleep(0.01)
#        print(f"==== GetStatus {i+1} ====")
        response = send_message_with_lrc(com_port, messageGetStatus)
        if not response:
            continue

        try:
            # Шукаємо JSON у відповіді
            response_str = response.decode('utf-8', errors='ignore')  # ігноримо сміття
            json_start = response_str.find("{")
            json_end = response_str.rfind("}") + 1

            if json_start != -1 and json_end != -1:
                json_part = response_str[json_start:json_end]
                response_dict = json.loads(json_part)

                if response_dict.get("status") == "S00": #in ("S04", "S05"):
                    time.sleep(2)
                    print("Отримано статус S00, відправляємо GetLastResult")
#                    send_message_with_lrc(com_port, messageInterrupt)
                    time.sleep(0.1)
                    send_message_with_lrc(com_port, messageGetLastResult)
                    time.sleep(1)
                    break
            else:
                print(f"⚠️ Не вдалося знайти JSON у відповіді: {response}")
        except Exception as e:
            print(f"Помилка при обробці відповіді: {e}, відповідь: {response}")
