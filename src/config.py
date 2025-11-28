"""
Модуль для конфигурации приложения
"""
DB_CONFIG = {
    'dbname': 'hh_vacancies',
    'user': 'postgres',
    'password': '123456',
    'host': 'localhost',
    'port': '5432'
}

# Список компаний для сбора данных
EMPLOYER_IDS = [
    '1740',    # Яндекс
    '2180',    # Ozon
    '3529',    # Сбер
    '15478',   # VK
    '78638',   # Тинькофф
    '84585',   # Авито
    '1057',    # Kaspersky
    '4181',    # 1C
    '1429999', # Selectel
    '1122462'  # Veeam Software
]

HH_API_URL = 'https://api.hh.ru/'
