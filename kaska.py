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
def check_status(host, port, max_attempts=5, delay=2):
    for attempt in range(max_attempts):
        response = send_message_with_lrc(host, port, messageGetStatus)
        try:
            # Перетворюємо байтову відповідь у словник
            response_dict = json.loads(response.decode('utf-8'))
            if response_dict.get("status") == "S00":
                print(f"Отримано статус S00 на спробі {attempt+1}")
                return True
            else:
                print(f"Отримано статус {response_dict.get('status')} на спробі {attempt+1}, чекаємо...")
        except json.JSONDecodeError:
            print(f"Помилка декодування JSON у відповіді: {response}")
        time.sleep(delay)  # Пауза між спробами
    print(f"Не вдалося отримати статус S00 після {max_attempts} спроб")
    return False


# # Повідомлення для відправки у сокет
# random_amount = str(random.randint(1000, 49999))
# merchant_ids = ["TG001079", "0173101"]
# random_merchantId = random.choice(merchant_ids)
# purchase_dict = {"method": "Purchase", "step": "0", "params": {"transAmount": random_amount, "transCurrency": "980", "merchantId": random_merchantId, "transactionUid": "2i89y0787308" }}

# # Перетворюємо словник у JSON-рядок і кодуємо в байти
# messagePurchase = json.dumps(purchase_dict).encode('utf-8')

#messagePurchase = b'{"method": "Purchase","step":"0","params": {"transAmount": "80000","transCurrency": "980", "merchantId": "TG001079","transactionUid": "2i89y0787308"}}' #, "discountedAmount": "38000", "step":"2", 

# messageRefund = b'{"method": "Refund", "params": {"transAmount": "700", "transCurrency": "980", "merchantId": "0173101", "rrn":"519718000159"}}'

# messageVoid = b'{"method": "Void", "params": {"invoiceNum": "800025", "transactionUid":"2i89y0787301"}}'

# messagePreauthorization = b'{"method": "Preauthorization","step":"0", "params": {"transAmount": "51000", "transCurrency": "980", "merchantId": "000000064008592"}}'

# messageSalePreauth = b'{"method": "SalePreauth", "params": {"transAmount": "51000", "transCurrency": "980", "authCode": "769700", "endAmount": "51000", "merchantId": "000000064008592", "rrn": "605351686477"}}'
# messageVoidPreauth= b'{"method": "VoidPreauth", "params": {"invoiceNum": "011035"}}'


# messageCash = b'{"method": "Cash","step":"0", "params": {"transAmount": "3000", "transCurrency": "980", "merchantId": "EXIM CASH      "}}'


# messageBalance = b'{"method": "Balance", "params": {"transCurrency": "980", "merchantId": "EXIM CASH      "}}'

# messageDeposit = b'{"method": "Deposit", "step":"0", "params": {"transAmount": "4000", "transCurrency": "980", "merchantId": "EXIM CASH      "}}'


messageGetLastResult = b'{"method": "GetLastResult"}'


messageGetStatus = b'{"method": "GetStatus"}'

# messagePingDevice = b'{"method": "PingDevice"}'

# messageCashBack = b'{"method": "CashBack","step":"0", "params": {"transAmount": "500000", "cashAmount":"120000","transCurrency": "980", "merchantId": "S1K80D7B1111111", "terminalId": "S1K80D7B"}}'

# messageGetLastReceipt = b'{"method": "GetLastReceipt"}'

# messageXReport = b'{"method": "XReport", "params": {"merchantId": "0173101", "isDetailReport": true}}' #, "params": {"merchantId": "ACDCSSI10000000", "isDetailReport": true}}' # , "isDetailReport": true
# messageZReport = b'{"method": "ZReport", "params": {"merchantId": "0173101"}}' #, "params": {"merchantId": "ACDCSSI10000000", "isDetailReport": true}}' # , "isDetailReport": "true"
messageGetLastReport = b'{"method": "GetLastReport"}'
# messageInterrupt = b'{"method": "Interrupt"}'
# messageRestartPaymentApp = b'{"method": "RestartPaymentApp"}'
# #messageEcho = b'{"method": "Echo", "params": {"merchantId": "TG001079"}}'
# messageGetMerchantList = b'{"method": "GetMerchantList"}'
# messageGetMerchantListDetailed = b'{"method": "GetMerchantListDetailed"}'
# messageGetLastReportReceipt = b'{"method": "GetLastReportReceipt"}'
# messageRestart = b'{"method": "ZReport"}'
# messageGetResultByUid = b'{"method": "GetResultByUid", "params": {"transactionUid": "2i89y0787308"}}'
# messageGetTerminalInfo = b'{"method": "GetTerminalInfo"}'

# Ваші дані для підключення до сокету
#host = '192.168.0.134' #Newland SP 000000064008592
#host = '192.168.0.132' #TP10 0173101 TG001079
#host = '192.168.0.54' # M3P "S990X001       "
host = '192.168.0.11' #X990 ACDCSSI10000000  12312312234tttt
port = 3000

#send_message_with_lrc(host, port, messagePurchase)

# Відправка повідомлення та очікування відповіді

#send_message_with_lrc(host, port, messageVoidPreauth)

#send_message_with_lrc(host, port, messageRefund)


#  messageGetLastResult  messagePurchase  messageVoid  messageRefund  messageGetStatus  messageCashBack  messagePreauthorization  messageSalePreauth messageVoidPreauth

#  messageInterrupt messagePingDevice  messageEcho  messageGetLastReceipt  messageGetMerchantList GetMultiPosBankListDetailed

#  messageGetLastReport  messageZReport  messageXReport  messageGetLastReportReceipt


#send_message_with_lrc(host, port, messageVoid)

#send_message_with_lrc(host, port, messageCash)
#send_message_with_lrc(host, port, messageBalance)
#send_message_with_lrc(host, port, messageDeposit)
#send_message_with_lrc(host,port, messageRestartPaymentApp)



#send_message_with_lrc(host, port, messagePreauthorization)


#parsed_data = parse_json(send_message_with_lrc(host, port, messageGetStatus))
#send_message_with_lrc(host, port, messageRefund)

#send_message_with_lrc(host, port, messagePreauthorization)
#send_message_with_lrc(host, port, messageCashBack)

#send_message_with_lrc(host, port, messageSalePreauth)


#send_message_with_lrc(host, port, messageGetLastReceipt)
#send_message_with_lrc(host, port, messagePurchase)
#send_message_with_lrc(host, port, messageXReport)

#send_message_with_lrc(host, port, messagePurchase)

#send_message_with_lrc(host, port, messagePingDevice)

#send_message_with_lrc(host, port, messageZReport)
#send_message_with_lrc(host, port, messageGetLastReport)


#send_message_with_lrc(host, port, messageGetLastResult)


###send_message_with_lrc(host, port, messageGetLastReceipt)
#
# #send_message_with_lrc(host, port, messageGetLastResult)
#
#
# #while 1:
# #   send_message_with_lrc(host, port, messageGetStatuse)

#send_message_with_lrc(host, port, messageGetStatus)

#send_message_with_lrc(host, port, messageInterrupt)




# import serial
#
# def calculate_lrc(message):
#      lrc = 0
#      for byte in message:
#          lrc ^= byte
#      return lrc

# def send_message_with_lrc(port, message):
#      # Відкриваємо COM-порт
#      ser = serial.Serial(port, baudrate=9600,   bytesize=serial.EIGHTBITS,  parity=serial.PARITY_NONE,   stopbits=serial.STOPBITS_ONE,timeout=1)
#  #     # Додаємо початкові байти до повідомлення
#      message_with_header = bytearray([0x02, 0x66, 0x01])
#  #     # Додаємо довжину повідомлення у вигляді двох байтів
#      message_length = len(message).to_bytes(2, byteorder='big')
#      message_with_header.extend(message_length)
#  #     # Додаємо саме повідомлення
#      message_with_header.extend(message)
#  #     # Обчислюємо LRC
#      lrc = calculate_lrc(message)
#      message_with_header.append(lrc)
#  #     # Відправляємо повідомлення через COM-порт
#      ser.write(message_with_header)
#  #     # Отримуємо та виводимо відповідь
#      response = ser.read(1024)
#      response_str = response
#      print("Отримана відповідь від сервера:", response_str)
#  #     # Закриваємо COM-порт
#      ser.close()
#  # # Повідомлення для відправки через COM-порт
# messageGetTerminalInfo = b'{"method": "GetTerminalInfo"}'
#  # # Ваш COM-порт (змініть на відповідний)
# com_port = 'COM35'
#  # # Відправка повідомлення та очікування відповіді
# send_message_with_lrc(com_port, messageGetStatus)

# #----------------------------------------------------------------

merchant_ids = ["TG001079", "0173101", "TG0010791111111","017310122222222"]
index = 0

if check_status(host, port):
    for i in range(4):
        transaction_uid = f"2i89y078762{i+1:01d}"
        random_amount = str(random.randint(40000, 79999))

        merchant_id = merchant_ids[index % len(merchant_ids)] #послідовна передача мерчантів
        index += 1
    
        random_merchantId = random.choice(merchant_ids)    #рендомна передача мерчантів
        purchase_dict = {"method": "Purchase", "step": "0", "params": {"transAmount": random_amount, "transCurrency": "980", "merchantId": "20900448", "transactionUid": transaction_uid }}
#       purchase_dict = {"method": "Echo", "params": {"merchantId": merchant_id}}
#        purchase_dict = {"method": "ZReport", "params": {"merchantId": merchant_id}}
# Перетворюємо словник у JSON-рядок і кодуємо в байти
        messagePurchase = json.dumps(purchase_dict).encode('utf-8')
        print(f"==== Початок циклу {i+1} ====")

    # Крок 1 — Надіслати Purchase
        send_message_with_lrc(host, port, messagePurchase)
        time.sleep(1)
        # Крок 3 — Повторити GetStatus до 6 разів з паузою 2 сек, якщо S00 не отримано
        for _ in range(30):
            response = send_message_with_lrc(host, port, messageGetStatus)
            try:
                response_dict = json.loads(response.decode('utf-8'))
                if response_dict.get("status") == "S00":
                    time.sleep(2)
                    print(f"Отримано статус S00 у кроці 3, відправляємо GetLastResult")
                    send_message_with_lrc(host, port, messageGetLastResult)
                    time.sleep(2)  # Пауза перед наступним циклом
                    break  # Перериваємо цикл після отримання S00
                #else:
                    #print(f"Отримано статус {response_dict.get('status')} у кроці 3")
            except json.JSONDecodeError:
                print(f"Помилка декодування JSON у відповіді: {response}")
            time.sleep(2)
        else:
            # Якщо S00 не отримано після всіх спроб, відправляємо GetLastResult
            print("Статус S00 !!!не отримано, відправляємо GetLastResult")
            send_message_with_lrc(host, port, messageGetLastResult)
            time.sleep(3)  # Пауза перед наступним циклом       
else:
    print("Цикл не запущено через відсутність статусу S00")
