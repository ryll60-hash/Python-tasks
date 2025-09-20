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

    response = ser.read(1024)  # читаємо відповідь
    ser.close()

    if response:
        print("Отримана відповідь від сервера:", response)
        return response
    else:
        print("⚠️ Від сервера не отримано відповіді")
        return None


# ======== Твої повідомлення =========
messagePurchase1 = b'{"method": "Purchase","step":"1","params": {"transAmount": "472000","transCurrency": "980", "merchantId": "20900448","transactionUid": "2i89y0787759"}}'
messagePurchase2 = b'{"method": "Purchase","step":"2","params": {"transAmount": "478000","transCurrency": "980", "merchantId": "20900448","transactionUid": "2i89y0787759"}}'
messageGetStatus  = b'{"method": "GetStatus"}'
messageGetLastResult = b'{"method": "GetLastResult"}'

com_port = 'COM8'

# ======== Основний цикл =========
for i in range(10):
    print(f"==== Початок циклу {i+1} ====")
    send_message_with_lrc(com_port, messagePurchase1)

    for i in range(40):
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

                if response_dict.get("status") == "S08":
                    time.sleep(2)
                    print("Отримано статус S08, відправляємо GetLastResult")
                    send_message_with_lrc(com_port, messageGetLastResult)
                    time.sleep(1)
                    break
            else:
                print(f"⚠️ Не вдалося знайти JSON у відповіді: {response}")
        except Exception as e:
            print(f"Помилка при обробці відповіді: {e}, відповідь: {response}")

    print("STEP 2 with new amount")
    time.sleep(0.2)
    send_message_with_lrc(com_port, messagePurchase2)

    for i in range(40):
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

                if response_dict.get("status") == "S00":
                    time.sleep(2)
                    print("Отримано статус S00, відправляємо GetLastResult")
                    send_message_with_lrc(com_port, messageGetLastResult)
                    time.sleep(1)
                    break
            else:
                print(f"⚠️ Не вдалося знайти JSON у відповіді: {response}")
        except Exception as e:
            print(f"Помилка при обробці відповіді: {e}, відповідь: {response}")
