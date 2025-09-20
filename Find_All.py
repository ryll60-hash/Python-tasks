import os
import re

def search_in_files(base_path, extensions, search_term):
    """
    Шукає файли з заданими розширеннями в базовій директорії та піддиректоріях.
    Перевіряє кожен файл на наявність терміну пошуку.

    :param base_path: Шлях до базової директорії.
    :param extensions: Список розширень файлів для пошуку (наприклад, [".txt", ".log"]).
    :param search_term: Термін для пошуку в файлах.
    """
    for root, _, files in os.walk(base_path):
        for file_name in files:
            # Перевіряємо розширення файлу
            if any(file_name.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file_name)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                        content = file.read()
                        if re.search(search_term, content):
                            print(f"Знайдено термін у файлі: {file_path}")
                except Exception as e:
                    print(f"Не вдалося відкрити файл {file_path}. Помилка: {e}")

# Приклад використання
base_directory = r"C:\Users\Zver\Desktop\Workspace\Укрпочта\Bags"  # Вкажіть ваш шлях
file_extensions = [".txt", ".log"]  # Вкажіть потрібні розширення
search_keyword = "PosSetreceiptNumber"  # Вкажіть термін для пошуку

search_in_files(base_directory, file_extensions, search_keyword)
