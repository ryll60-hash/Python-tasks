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


def calculate_lrc(message):
     lrc =0
     for byte in message:
         lrc ^= byte
     return lrc
def send_message_with_lrc(host, port, message):
     # Додаємо початкові байти до повідомлення
     message_with_header = bytearray([0x02, 0x66, 0x01])
      # Додаємо довжину повідомлення у вигляді двох байтів
     message_length = len(message).to_bytes(2, byteorder='big')
     message_with_header.extend(message_length)
 #      # Додаємо саме повідомлення
     message_with_header.extend(message)
      # Обчислюємо LRC
     lrc = calculate_lrc(message)
     message_with_header.append(lrc)
      # Відправляємо повідомлення у сокет
     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
         s.connect((host, port))
         s.sendall(message_with_header)

          # Очікуємо відповідь від сервера
         response = s.recv(10240)  # Максимальний розмір даних для отримання - 10240 байти
         response_str = response#.decode('utf-8')  # Переводимо байтовий рядок у рядок формату Unicode (str)
         print("Отримана відповідь від сервера:", response_str[5:-1])
         return response_str[5:-1]

messagePurchase1 = b'{"method": "Purchase","step":"0","params": {"transAmount": "47200","transCurrency": "980", "merchantId": "20900448","transactionUid": "2289y0787759"}}' #, "discountedAmount": "38000", "step":"2", 

messageRefund = b'{"method": "Refund", "params": {"transAmount": "52830", "transCurrency": "980", "merchantId": "ACDCSSI10000000", "rrn":"944409193592"}}' #, "transactionUid":"2i89y0787301"

messageVoid = b'{"method": "Void", "params": {"invoiceNum": "001901", "transactionUid":"2i89y0787819"}}'

messagePreauthorization = b'{"method": "Preauthorization","step":"0", "params": {"transAmount": "51000", "transCurrency": "980", "merchantId": "000000064008592"}}'

messageSalePreauth = b'{"method": "SalePreauth", "params": {"transAmount": "51000", "transCurrency": "980", "authCode": "769700", "endAmount": "51000", "merchantId": "000000064008592", "rrn": "605351686477"}}'
messageVoidPreauth= b'{"method": "VoidPreauth", "params": {"invoiceNum": "011035"}}'


messageCash = b'{"method": "Cash","step":"0", "params": {"transAmount": "3000", "transCurrency": "980", "merchantId": "EXIM CASH      "}}'


messageBalance = b'{"method": "Balance", "params": {"transCurrency": "980", "merchantId": "EXIM CASH      "}}'

messageDeposit = b'{"method": "Deposit", "step":"0", "params": {"transAmount": "4000", "transCurrency": "980", "merchantId": "EXIM CASH      "}}'


messageGetLastResult = b'{"method": "GetLastResult"}'


messageGetStatus = b'{"method": "GetStatus"}'

messagePingDevice = b'{"method": "PingDevice"}'

messageCashBack = b'{"method": "CashBack","step":"0", "params": {"transAmount": "200000", "cashAmount":"120000","transCurrency": "980", "merchantId": "TG001079", "terminalId": "TG001079","transactionUid": "2i89y0787433"}}'

messageGetLastReceipt = b'{"method": "GetLastReceipt"}'

messageXReport = b'{"method": "XReport", "params": {"merchantId": "TG001079"}}' #, "params": {"merchantId": "ACDCSSI10000000", "isDetailReport": true}}' # , "isDetailReport": true
messageZReport = b'{"method": "ZReport", "params": {"merchantId": "TG0010791111111"}}' #, "params": {"merchantId": "ACDCSSI10000000", "isDetailReport": true}}' # , "isDetailReport": "true"
messageZReport1 = b'{"method": "ZReport", "params": {"merchantId": "017310122222222"}}'
messageGetLastReport = b'{"method": "GetLastReport"}'
messageInterrupt = b'{"method": "Interrupt"}'
messageRestartPaymentApp = b'{"method": "RestartPaymentApp"}'
messageEcho = b'{"method": "Echo", "params": {"merchantId": "TG001079"}}'
messageEcho1 = b'{"method": "Echo", "params": {"merchantId": "0173101"}}'
messageGetMerchantList = b'{"method": "GetMerchantList"}'
messageGetMultiPosBankListDetailed = b'{"method": "GetMultiPosBankListDetailed"}'
messageGetLastReportReceipt = b'{"method": "GetLastReportReceipt"}'
messageRestart = b'{"method": "Restart"}'
messageGetResultByUid = b'{"method": "GetResultByUid", "params": {"transactionUid": "2i89y0787623"}}' #2i89y0787318  2i89y0787412
messageGetTerminalInfo = b'{"method": "GetTerminalInfo"}'

# Ваші дані для підключення до сокету
#host = '192.168.0.134' #Newland SP 000000064008592
#host = '192.168.0.132' #TP10 0173101 TG001079
#host = '192.168.0.54' # M3P "S990X001       "
host = '192.168.0.11' #X990 ACDCSSI10000000  12312312234tttt Multipos: Aval(6500121), Oshad (20900448), FUIB (777777777777), Mono (ACDCSSI10000000), MTB (7777798)
port = 3000

#send_message_with_lrc(host, port, messageGetStatus)

# Відправка повідомлення та очікування відповіді

#send_message_with_lrc(host, port, messageVoidPreauth)

#send_message_with_lrc(host, port, messageRefund)


#  messageGetLastResult  messagePurchase  messageVoid  messageRefund messageCashBack  messagePreauthorization  messageSalePreauth messageVoidPreauth

#  messageInterrupt messagePingDevice  messageEcho  messageGetLastReceipt  messageGetMerchantList messageGetMultiPosBankListDetailed messageGetStatus

#  messageGetLastReport  messageZReport  messageXReport  messageGetLastReportReceipt

for i in range(4):
    print(f"==== Початок циклу {i+1} ====")
    send_message_with_lrc(host, port, messagePurchase1)
#    time.sleep(2)
    for i in range(20):
        time.sleep(1)
        print(f"==== GetStatus {i+1} ====")
        response = send_message_with_lrc(host, port, messageGetStatus)
        try:
            response_dict = json.loads(response.decode('utf-8'))
            if response_dict.get("status") == "S04":
                    time.sleep(0.5)
                    print(f"Отримано статус S04 у кроці 3, відправляємо messageInterrupt")
                    send_message_with_lrc(host, port, messageInterrupt)
                    time.sleep(1)  # Пауза перед наступним циклом
                    break  # Перериваємо цикл після отримання S00
        except json.JSONDecodeError:
                print(f"Помилка декодування JSON у відповіді: {response}")