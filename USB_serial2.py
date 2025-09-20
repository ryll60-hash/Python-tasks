import socket
import serial
import time
import json
import random

def parse_json(json_string):
    """
    Parse a JSON string and return a dictionary.
    """
    try:
        # Convert JSON string to dictionary
        data = json.loads(json_string)
        return data
    except json.JSONDecodeError:
        # Handle the exception if JSON is invalid
        return "Invalid JSON"
    
     # Повідомлення для відправки у сокет
messagePurchase = b'{"method": "Purchase", "step":"1", "params": {"transAmount": "45000", "transCurrency": "980", "merchantId": "20900448", "transactionUid": "2i89y0787419"}}' #, "discountedAmount": "38000", "step":"1",
messageRefund = b'{"method": "Refund", "params": {"transAmount": "3000", "transCurrency": "980", "merchantId": "20900448", "authCode": "983044", "rrn":"944409177869" }}' # "rrn":"944409192875"
messageVoid = b'{"method": "Void", "params": {"invoiceNum": "100063"}}'
messagePreauthorization = b'{"method": "Preauthorization", "params": {"transAmount": "5000", "transCurrency": "980", "merchantId": "TG001079"}}'
messageSalePreauth = b'{"method": "SalePreauth", "params": {"transAmount": "500", "transCurrency": "980", "authCode": "467997", "endAmount": "500", "merchantId": "000000064008592", "rrn": "427100009890"}}'
messageVoidPreauth= b'{"method": "VoidPreauth", "params": {"invoiceNum": "585130"}}'
messageCash = b'{"method": "Cash", "params": {"transAmount": "51000", "transCurrency": "980", "merchantId": "EXIM CASH      "}}'
messageBalance = b'{"method": "Balance", "params": {"transCurrency": "980", "merchantId": "EXIM CASH      "}}'
messageDeposit = b'{"method": "Deposit", "params": {"transAmount": "1000", "transCurrency": "980", "merchantId": "EXIM CASH      "}}'
messageGetLastResult = b'{"method": "GetLastResult"}'
messageGetStatus = b'{"method": "GetStatus"}'
messagePingDevice = b'{"method": "PingDevice"}'
messageCashBack = b'{"method": "CashBack", "step":"0", "params": {"transAmount": "5000", "cashAmount":"3000","transCurrency": "980", "merchantId": "20900448"}}'
messageGetLastReceipt = b'{"method": "GetLastReceipt"}'
messageXReport = b'{"method": "XReport", "params": {"merchantId": "20900448"}}' # , "isDetailReport": "true"
messageZReport = b'{"method": "ZReport", "params": {"merchantId": "6500121"}}' # , "isDetailReport": "true"
messageGetLastReport = b'{"method": "GetLastReport"}'
messageInterrupt = b'{"method": "Interrupt"}'
messageRestartPaymentApp = b'{"method": "RestartPaymentApp"}'
messageEcho = b'{"method": "Echo", "params": {"merchantId": "6500121"}}'
messageGetMerchantList = b'{"method": "GetMerchantList"}'
messageGetLastReportReceipt = b'{"method": "GetLastReportReceipt"}'
messageGetResultByUid = b'{"method": "GetResultByUid", "params": {"transactionUid": "2i89y0787721"}}'
messageRestart = b'{"method": "Restart"}'


def calculate_lrc(message):
     lrc = 0
     for byte in message:
         lrc ^= byte
     return lrc

def send_message_with_lrc(port, message):
     # Відкриваємо COM-порт
     ser = serial.Serial(port, baudrate=9600,   bytesize=serial.EIGHTBITS,  parity=serial.PARITY_NONE,   stopbits=serial.STOPBITS_ONE,timeout=1)
 #     # Додаємо початкові байти до повідомлення
     message_with_header = bytearray([0x02, 0x66, 0x01])
 #     # Додаємо довжину повідомлення у вигляді двох байтів
     message_length = len(message).to_bytes(2, byteorder='big')
     message_with_header.extend(message_length)
 #     # Додаємо саме повідомлення
     message_with_header.extend(message)
 #     # Обчислюємо LRC
     lrc = calculate_lrc(message)
     message_with_header.append(lrc)
 #     # Відправляємо повідомлення через COM-порт
     ser.write(message_with_header)
 #     # Отримуємо та виводимо відповідь
     response = ser.read(1024)
     response_str = response
     print("Отримана відповідь від сервера:", response_str)
 #     # Закриваємо COM-порт
     ser.close()
 # # Повідомлення для відправки через COM-порт
#messageGetTerminalInfo = b'{"method": "GetTerminalInfo"}'
#messageEcho = b'{"method": "Echo", "params": {"merchantId": "S990X001       "}}'
 # # Ваш COM-порт (змініть на відповідний)
com_port = 'COM8' #TP10 '0173101' 'COmessageGetStatusM43' Multipos: Aval(6500121), Oshad (20900448), FUIB (777777777777), Mono (ACDCSSI10000000), MTB (7777798)
 # # Відправка повідомлення та очікування відповіді

send_message_with_lrc(com_port, messageGetStatus)

#  messageGetLastResult  messagePurchase  messageVoid  messageRefund  messageCashBack  messagePreauthorization

#  messageInterrupt messagePingDevice  messageEcho  messageGetLastReceipt  messageGetMerchantList messageGetStatus

#  messageGetLastReport  messageZReport  messageXReport  messageGetLastReportReceipt


#merchant_ids = ["20900448", "6500121","ACDCSSI10000000", "7777798"]
#index = 0


# for i in range(1):
#     transaction_uid = f"2i89y078764{i+1:01d}"
#     random_amount = str(random.randint(1000, 49999))
# #    merchant_id = merchant_ids[index % len(merchant_ids)]
# #    index += 1
    
# #    random_merchantId = random.choice(merchant_ids)
#     purchase_dict = {"method": "Purchase", "step": "0", "params": {"transAmount": random_amount, "transCurrency": "980", "merchantId": "20900448", "transactionUid": transaction_uid }}

# # Перетворюємо словник у JSON-рядок і кодуємо в байти
#     messagePurchase = json.dumps(purchase_dict).encode('utf-8')
#     print(f"==== Початок циклу {i+1} ====")

#     # Крок 1 — Надіслати Purchase
#     send_message_with_lrc(com_port, messagePurchase)
#     time.sleep(1)

#     # Крок 2 — Повторити GetStatus 7 разів з паузою 2 сек
#     for _ in range(2):
#         send_message_with_lrc(com_port, messageGetStatus)
#         time.sleep(3)

#     # Крок 3 — Повторити GetStatus 6 разів з паузою 3 сек
#     for _ in range(10):
#         send_message_with_lrc(com_port, messageGetStatus)
#         time.sleep(2)

#     # Крок 4 — Надіслати GetLastResult
#     send_message_with_lrc(com_port, messageGetLastResult)
#     time.sleep(2)  # Пауза перед наступним циклом (за бажанням)
