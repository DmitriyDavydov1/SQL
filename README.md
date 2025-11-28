Поиск вакансий
Описание
Проект для сбора и анализа данных о вакансиях и компаниях с сайта hh.ru с использованием PostgreSQL для хранения данных.

Он позволяет найти подходящие вакансии на основе заданных ключевых слов и города.
Сортирует вакансии по зарплате.
Выводит все вакансии или интересующий Топ.

Функциональность
Сбор данных: Автоматический сбор информации о компаниях и вакансиях с HH.ru через API.
Хранение данных: Сохранение данных в реляционной базе PostgreSQL с продуманной схемой.
Анализ данных: Готовые методы для анализа вакансий и компаний.
Поиск: Поиск вакансий по ключевым словам.
Статистика: Получение статистики по зарплатам и количеству вакансий.

Проект включает в себя следующие модули:
config.py
database.py
db_manager.py
hh_api.py
main.py

Обзор функциональных модулей:
main.py
Основной модуль, обеспечивающий запуск приложения и демонстрацию работы с объектами.
config.py
Конфигурация приложения
database.py
Модуль для управления БД
db_manager.py
Класс для работы с данными в БД
hh_api.py
Модуль для работы с API hh.ru

API методы
Класс DBManager предоставляет следующие методы для работы с данными:

1. Компании и количество вакансий
manager.get_companies_and_vacancies_count()
Возвращает: Список компаний с количеством вакансий

2. Все вакансии
manager.get_all_vacancies()
Возвращает: Полный список вакансий с информацией о компании, зарплате и ссылке

3. Средняя зарплата
manager.get_avg_salary()
Возвращает: Среднюю зарплату по всем вакансиям

4. Вакансии с высокой зарплатой
manager.get_vacancies_with_higher_salary()
Возвращает: Вакансии с зарплатой выше средней

5. Поиск по ключевым словам
manager.get_vacancies_with_keyword('python')
Возвращает: Вакансии, содержащие ключевое слово в названии

Зависимости
Версия
python = "^3.12"
requests = "^2.32.5"
python-dotenv = "^1.2.1"
pandas = "^2.3.3"
openpyxl = "^3.1.5"
psycopg2-binary = "^2.9.11"
flake8 = "^7.3.0"
pytest = "^9.0.1"
pytest-cov = "^7.0.0"
mypy = "^1.18.2"
black = "^25.11.0"
isort = "^7.0.0"

Установка
Клонируйте репозиторий:
https://github.com/DmitriyDavydov1/SQL.git

Настройка базы данных
CREATE DATABASE hh_vacancies ENCODING 'UTF8';

Настройте подключение
Отредактируйте файл src/config.py:
DB_CONFIG = {
    'dbname': 'hh_vacancies',
    'user': 'postgres', 
    'password': '123456',  # Замените на ваш пароль
    'host': 'localhost',
    'port': '5432'
}

Установите зависимости:
pip install package-name
poetry install
poetry add --group dev flake8
poetry add --group lint mypy
poetry add --group lint black
poetry add --group lint isort
poetry add python-dotenv
poetry add pandas
poetry add openpyxl
poetry add psycopg2-binary
pip install pytest pytest-cov requests-mock

Тестирование проекта
Тестирование проекта проводится с использованием пакета tests, который включает следующие файлы:
conftest.py
test_database.py
test_db_manager.py
test_hh_api.py
test_main.py

Запуск с подробным отчетом о покрытии
python -m pytest tests/ -v --cov=src --cov-report=html

Связи между таблицами
vacancies.employer_id → employers.employer_id (один-ко-многим)
ON DELETE CASCADE - при удалении компании удаляются все её вакансии

Конфигурация
Настройка компаний для сбора
В файле src/config.py можно изменить список компаний:
EMPLOYER_IDS = [
    '1740',    # Яндекс
    '2180',    # Ozon
    # Добавьте свои компании...
]
Получение ID компании
Перейдите на страницу компании на HH.ru
URL будет выглядеть так: https://hh.ru/employer/1740
Число в конце URL - это ID компании (в примере: 1740)

Запуск программы
python src/main.py
