"""
Модуль для работы с базой данных PostgreSQL
"""
import psycopg2
from config import DB_CONFIG


class DatabaseManager:
    """Класс для управления базой данных"""

    def __init__(self):
        self.config = DB_CONFIG
        self.conn = None
        self.cur = None

    def connect(self):
        """Устанавливает соединение с базой данных"""
        try:
            self.conn = psycopg2.connect(**self.config)
            self.cur = self.conn.cursor()
            print("Успешное подключение к базе данных")
            return True
        except psycopg2.OperationalError as e:
            print(f"Ошибка подключения к базе данных: {e}")
            print("Проверьте:")
            print("1. Запущен ли PostgreSQL")
            print("2. Правильность параметров в config.py")
            print("3. Существует ли база данных 'hh_vacancies'")
            return False

    def create_tables(self):
        """Создает таблицы в базе данных"""
        try:
            # Таблица работодателей
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS employers (
                    employer_id VARCHAR(20) PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    area VARCHAR(100),
                    site_url VARCHAR(255),
                    open_vacancies INTEGER
                )
            """)

            # Таблица вакансий
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS vacancies (
                    vacancy_id VARCHAR(20) PRIMARY KEY,
                    employer_id VARCHAR(20) REFERENCES employers(employer_id) ON DELETE CASCADE,
                    name VARCHAR(255) NOT NULL,
                    salary_from INTEGER,
                    salary_to INTEGER,
                    url VARCHAR(255),
                    area VARCHAR(100),
                    published_at TIMESTAMP
                )
            """)

            self.conn.commit()
            print("Таблицы созданы успешно")
            return True

        except psycopg2.Error as e:
            print(f"Ошибка при создании таблиц: {e}")
            return False

    def clear_tables(self):
        """Очищает таблицы перед заполнением"""
        try:
            self.cur.execute("DELETE FROM vacancies")
            self.cur.execute("DELETE FROM employers")
            self.conn.commit()
            print("Таблицы очищены")
        except psycopg2.Error as e:
            print(f"Ошибка при очистке таблиц: {e}")

    def insert_employer(self, employer):
        """Добавляет работодателя в таблицу"""
        try:
            self.cur.execute("""
                INSERT INTO employers (employer_id, name, description, area, site_url, open_vacancies)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                employer['id'],
                employer['name'],
                employer.get('description', '')[:1000],  # Ограничиваем длину
                employer.get('area', ''),
                employer.get('site_url', ''),
                employer.get('open_vacancies', 0)
            ))
            return True
        except psycopg2.Error as e:
            print(f"Ошибка при добавлении работодателя {employer['name']}: {e}")
            return False

    def insert_vacancy(self, vacancy):
        """Добавляет вакансию в таблицу"""
        try:
            self.cur.execute("""
                INSERT INTO vacancies (vacancy_id, employer_id, name, salary_from, salary_to, url, area, published_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                vacancy['id'],
                vacancy['employer_id'],
                vacancy['name'],
                vacancy.get('salary_from'),
                vacancy.get('salary_to'),
                vacancy.get('url', ''),
                vacancy.get('area', ''),
                vacancy.get('published_at')
            ))
            return True
        except psycopg2.Error as e:
            print(f"Ошибка при добавлении вакансии {vacancy['name']}: {e}")
            return False

    def fill_database(self, employers, vacancies):
        """Заполняет базу данных"""
        print("Заполнение базы данных...")

        success_employers = 0
        success_vacancies = 0

        # Добавляем работодателей
        for employer in employers:
            if self.insert_employer(employer):
                success_employers += 1

        # Добавляем вакансии
        for vacancy in vacancies:
            if self.insert_vacancy(vacancy):
                success_vacancies += 1

        self.conn.commit()
        print(f"База данных заполнена: {success_employers} компаний, {success_vacancies} вакансий")
        return success_employers > 0

    def close(self):
        """Закрывает соединение с базой данных"""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
            print("Соединение с базой данных закрыто")
