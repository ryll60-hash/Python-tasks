#name = input ("введитесвое имя: ")
#age = input ("укажите свой возвраст: ")

#print("Привте " + name + "!")
#print ("Тебе уже " + age + " лет, ничего все только начинается !!!!")
#input()
#____

# if 5 > 2:
#     print ("good mood")
def hex_to_text(hex_string):
    # Прибираємо пробіли і переводимо в байти
    hex_string = hex_string.replace(" ", "")
    bytes_object = bytes.fromhex(hex_string)
    # Конвертуємо у текст (ASCII/UTF-8)
    return bytes_object.decode("utf-8", errors="replace")

# Приклад використання
hex_data = "56 45 52 49 46 4F 4E 45 1C 54 35 50 52 56 61 5F 30 34 4D 1C 30 32 36 31 2D 32 30 31 2D 34 30 37 1C 53 25 31 1C 30 32 33 45 35 30 41 31 38 46 34 42 30 31"
# "S%1" appears in the hex string as: 53 25 31
# 53 = 'S', 25 = '%', 31 = '1'
#hex_data = "49 4D 45 49 33 35 38 31 32 39 30 36 38 34 32 35 35 31 36 2D"

text = hex_to_text(hex_data)
print("Результат:", text)



hex_data = "D09AD196D180D0B8D0BB20D087D0B4D0B7D18FD0BA27D18FD0BED0B2 " #поле 47 декодує EXIM
decoded_data = bytes.fromhex(hex_data).decode("utf-8")
print(decoded_data)


# # Байтова послідовність
byte_sequence = b'\xd0\x9d\xd0\x95\xd0\x94\xd0\x9e\xd0\xa1\xd0\xa2\xd0\x90\xd0\xa2\xd0\x9d\xd0\xac\xd0\x9e \xd0\x9a\xd0\x9e\xd0\xa8\xd0\xa2\xd0\x86\xd0\x92'


# # Декодування з UTF-8
decoded_text = byte_sequence.decode('utf-8')
print(decoded_text)


