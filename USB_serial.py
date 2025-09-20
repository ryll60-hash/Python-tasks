import serial
import datetime
import json
import os

def calculate_lrc(message):
    """Обчислює LRC для переданого повідомлення."""
    lrc = 0
    for byte in message:
        lrc ^= byte
    return lrc

def log_to_file(data, log_file="C:/Python_logs/terminal_logs.txt"):
    """Логування даних у файл."""
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    with open(log_file, "a") as file:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"{timestamp} - {data}\n")

def send_message_with_lrc(port, message, log_file="C:/Python_logs/terminal_logs.txt"):
    """Відправляє повідомлення через COM-порт із LRC та логуванням."""
    try:
        # Відкриваємо COM-порт
        ser = serial.Serial(port, baudrate=9600, bytesize=serial.EIGHTBITS,
                            parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=1)

        # Додаємо початкові байти до повідомлення
        message_with_header = bytearray([0x02, 0x66, 0x01])

        # Додаємо довжину повідомлення у вигляді двох байтів
        message_length = len(message).to_bytes(2, byteorder='big')
        message_with_header.extend(message_length)

        # Додаємо саме повідомлення
        message_with_header.extend(message)

        # Обчислюємо LRC
        lrc = calculate_lrc(message_with_header)
        message_with_header.append(lrc)

        # Відправляємо повідомлення через COM-порт
        ser.write(message_with_header)
        log_to_file(f"Відправлено: {message_with_header.hex()}", log_file)

        # Отримуємо відповідь
        response = ser.read(1024)
        log_to_file(f"Отримано: {response.hex()}", log_file)
        print("Отримана відповідь від сервера:", response.hex())

        # Закриваємо COM-порт
        ser.close()
    except serial.SerialException as e:
        log_to_file(f"Помилка COM-порту: {e}", log_file)
        print(f"Помилка COM-порту: {e}")

# Приклад використання
com_port = 'COM35'
messageGetLastResult = b'{"method": "GetLastResult"}'
send_message_with_lrc(com_port, messageGetLastResult)
