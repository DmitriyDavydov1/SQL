"""
Класс DBManager для работы с данными в БД
"""
import psycopg2
from config import DB_CONFIG


class DBManager:
    """Класс для работы с данными в БД"""

    def __init__(self):
        self.config = DB_CONFIG
        self.conn = None
        self.cur = None

    def connect(self):
        """Подключается к базе данных"""
        try:
            self.conn = psycopg2.connect(**self.config)
            self.cur = self.conn.cursor()
            return True
        except psycopg2.Error as e:
            print(f"Ошибка подключения: {e}")
            return False

    def get_companies_and_vacancies_count(self):
        """Получает список компаний и количество вакансий"""
        try:
            self.cur.execute("""
                SELECT e.name, COUNT(v.vacancy_id) 
                FROM employers e
                LEFT JOIN vacancies v ON e.employer_id = v.employer_id
                GROUP BY e.name
                ORDER BY COUNT(v.vacancy_id) DESC
            """)
            return self.cur.fetchall()
        except psycopg2.Error as e:
            print(f"Ошибка запроса: {e}")
            return []

    def get_all_vacancies(self):
        """Получает все вакансии"""
        try:
            self.cur.execute("""
                SELECT e.name, v.name, v.salary_from, v.salary_to, v.url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.employer_id
                ORDER BY e.name, v.name
            """)
            return self.cur.fetchall()
        except psycopg2.Error as e:
            print(f"Ошибка запроса: {e}")
            return []

    def get_avg_salary(self):
        """Получает среднюю зарплату"""
        try:
            self.cur.execute("""
                SELECT AVG((COALESCE(salary_from, 0) + COALESCE(salary_to, 0)) / 2)
                FROM vacancies
                WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL
            """)
            result = self.cur.fetchone()
            return round(float(result[0] or 0), 2) if result else 0
        except psycopg2.Error as e:
            print(f"Ошибка запроса: {e}")
            return 0

    def get_vacancies_with_higher_salary(self):
        """Получает вакансии с зарплатой выше средней"""
        try:
            self.cur.execute("""
                SELECT e.name, v.name, v.salary_from, v.salary_to, v.url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.employer_id
                WHERE (COALESCE(salary_from, 0) + COALESCE(salary_to, 0)) / 2 > (
                    SELECT AVG((COALESCE(salary_from, 0) + COALESCE(salary_to, 0)) / 2)
                    FROM vacancies
                    WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL
                )
                ORDER BY (COALESCE(v.salary_from, 0) + COALESCE(v.salary_to, 0)) / 2 DESC
            """)
            return self.cur.fetchall()
        except psycopg2.Error as e:
            print(f"Ошибка запроса: {e}")
            return []

    def get_vacancies_with_keyword(self, keyword):
        """Ищет вакансии по ключевому слову"""
        try:
            self.cur.execute("""
                SELECT e.name, v.name, v.salary_from, v.salary_to, v.url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.employer_id
                WHERE LOWER(v.name) LIKE LOWER(%s)
                ORDER BY e.name, v.name
            """, (f'%{keyword}%',))
            return self.cur.fetchall()
        except psycopg2.Error as e:
            print(f"Ошибка запроса: {e}")
            return []

    def close(self):
        """Закрывает соединение"""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
