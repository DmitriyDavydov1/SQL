"""
Тесты для модуля db_manager.py
"""
import pytest
import psycopg2
import sys
import os

# Добавляем src в путь для импорта
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.db_manager import DBManager
from src.config import DB_CONFIG


class TestDBManager:
    """Тесты для класса DBManager"""

    @pytest.fixture
    def db_manager(self):
        return DBManager()

    def test_init(self, db_manager):
        """Тест инициализации DBManager"""
        assert db_manager.config == DB_CONFIG
        assert db_manager.conn is None
        assert db_manager.cur is None

    def test_connect_success(self, db_manager, monkeypatch):
        """Тест успешного подключения"""

        class MockConnection:
            pass

        class MockCursor:
            pass

        def mock_connect(**kwargs):
            conn = MockConnection()
            conn.cursor = lambda: MockCursor()
            return conn

        monkeypatch.setattr('psycopg2.connect', mock_connect)

        result = db_manager.connect()
        assert result is True
        assert db_manager.conn is not None
        assert db_manager.cur is not None

    def test_connect_failure(self, db_manager, monkeypatch):
        """Тест неудачного подключения"""

        def mock_connect(**kwargs):
            raise psycopg2.OperationalError("Connection failed")

        monkeypatch.setattr('psycopg2.connect', mock_connect)

        result = db_manager.connect()
        assert result is False

    def test_get_companies_and_vacancies_count(self, db_manager, monkeypatch):
        """Тест получения компаний и количества вакансий"""
        mock_data = [
            ('Company A', 10),
            ('Company B', 5),
            ('Company C', 3)
        ]

        class MockCursor:
            def execute(self, query):
                pass

            def fetchall(self):
                return mock_data

        class MockConnection:
            def cursor(self):
                return MockCursor()

        monkeypatch.setattr('psycopg2.connect', lambda **kwargs: MockConnection())
        db_manager.connect()

        result = db_manager.get_companies_and_vacancies_count()

        assert result == mock_data
        assert len(result) == 3
        assert result[0][0] == 'Company A'
        assert result[0][1] == 10

    def test_get_all_vacancies(self, db_manager, monkeypatch):
        """Тест получения всех вакансий"""
        mock_data = [
            ('Company A', 'Python Developer', 100000, 150000, 'url1'),
            ('Company B', 'Java Developer', 120000, None, 'url2')
        ]

        class MockCursor:
            def execute(self, query):
                pass

            def fetchall(self):
                return mock_data

        class MockConnection:
            def cursor(self):
                return MockCursor()

        monkeypatch.setattr('psycopg2.connect', lambda **kwargs: MockConnection())
        db_manager.connect()

        result = db_manager.get_all_vacancies()

        assert result == mock_data
        assert len(result) == 2
        assert result[0][1] == 'Python Developer'
        assert result[0][2] == 100000

    def test_get_avg_salary(self, db_manager, monkeypatch):
        """Тест получения средней зарплаты"""

        class MockCursor:
            def execute(self, query):
                pass

            def fetchone(self):
                return (125000.50,)

        class MockConnection:
            def cursor(self):
                return MockCursor()

        monkeypatch.setattr('psycopg2.connect', lambda **kwargs: MockConnection())
        db_manager.connect()

        result = db_manager.get_avg_salary()

        assert result == 125000.50
        assert isinstance(result, float)

    def test_get_avg_salary_no_data(self, db_manager, monkeypatch):
        """Тест получения средней зарплаты при отсутствии данных"""

        class MockCursor:
            def execute(self, query):
                pass

            def fetchone(self):
                return (None,)

        class MockConnection:
            def cursor(self):
                return MockCursor()

        monkeypatch.setattr('psycopg2.connect', lambda **kwargs: MockConnection())
        db_manager.connect()

        result = db_manager.get_avg_salary()

        assert result == 0

    def test_get_vacancies_with_higher_salary(self, db_manager, monkeypatch):
        """Тест получения вакансий с зарплатой выше средней"""
        mock_data = [
            ('Company A', 'Senior Developer', 200000, 250000, 'url1'),
            ('Company B', 'Team Lead', 180000, 220000, 'url2')
        ]

        class MockCursor:
            def execute(self, query):
                pass

            def fetchall(self):
                return mock_data

        class MockConnection:
            def cursor(self):
                return MockCursor()

        monkeypatch.setattr('psycopg2.connect', lambda **kwargs: MockConnection())
        db_manager.connect()

        result = db_manager.get_vacancies_with_higher_salary()

        assert result == mock_data
        assert len(result) == 2
        assert result[0][1] == 'Senior Developer'
        assert result[0][2] == 200000

    def test_get_vacancies_with_keyword(self, db_manager, monkeypatch):
        """Тест поиска вакансий по ключевому слову"""
        mock_data = [
            ('Company A', 'Python Developer', 100000, 150000, 'url1'),
            ('Company B', 'Python Data Scientist', 120000, 180000, 'url2')
        ]

        class MockCursor:
            def execute(self, query, params):
                assert 'python' in params[0].lower()
                pass

            def fetchall(self):
                return mock_data

        class MockConnection:
            def cursor(self):
                return MockCursor()

        monkeypatch.setattr('psycopg2.connect', lambda **kwargs: MockConnection())
        db_manager.connect()

        result = db_manager.get_vacancies_with_keyword('python')

        assert result == mock_data
        assert len(result) == 2
        # Проверяем что все вакансии содержат Python в названии
        assert all('Python' in vacancy[1] for vacancy in result)

    def test_get_vacancies_with_keyword_no_results(self, db_manager, monkeypatch):
        """Тест поиска вакансий по ключевому слову без результатов"""

        class MockCursor:
            def execute(self, query, params):
                pass

            def fetchall(self):
                return []

        class MockConnection:
            def cursor(self):
                return MockCursor()

        monkeypatch.setattr('psycopg2.connect', lambda **kwargs: MockConnection())
        db_manager.connect()

        result = db_manager.get_vacancies_with_keyword('nonexistent')

        assert result == []
        assert len(result) == 0

    def test_close_connection(self, db_manager, monkeypatch):
        """Тест закрытия соединения"""
        closed = {'cursor': False, 'connection': False}

        class MockCursor:
            def close(self):
                closed['cursor'] = True

        class MockConnection:
            def cursor(self):
                return MockCursor()

            def close(self):
                closed['connection'] = True

        monkeypatch.setattr('psycopg2.connect', lambda **kwargs: MockConnection())
        db_manager.connect()

        db_manager.close()

        assert closed['cursor'] is True
        assert closed['connection'] is True
