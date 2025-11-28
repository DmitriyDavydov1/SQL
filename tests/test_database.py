"""
Тесты для модуля database.py
"""
import pytest
import psycopg2
import sys
import os

# Добавляем src в путь для импорта
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.database import DatabaseManager
from src.config import DB_CONFIG


class TestDatabaseManager:
    """Тесты для класса DatabaseManager"""

    @pytest.fixture
    def db_manager(self):
        return DatabaseManager()

    @pytest.fixture
    def test_employers(self):
        return [
            {
                'id': '1',
                'name': 'Company 1',
                'description': 'Desc 1',
                'area': 'Moscow',
                'site_url': 'https://company1.com',
                'open_vacancies': 5
            },
            {
                'id': '2',
                'name': 'Company 2',
                'description': 'Desc 2',
                'area': 'SPb',
                'site_url': 'https://company2.com',
                'open_vacancies': 3
            }
        ]

    @pytest.fixture
    def test_vacancies(self):
        return [
            {
                'id': 'v1',
                'name': 'Developer 1',
                'employer_id': '1',
                'salary_from': 100000,
                'salary_to': 150000,
                'url': 'https://hh.ru/v1',
                'area': 'Moscow',
                'published_at': '2023-12-01T10:00:00+0300'
            },
            {
                'id': 'v2',
                'name': 'Developer 2',
                'employer_id': '2',
                'salary_from': 120000,
                'salary_to': None,
                'url': 'https://hh.ru/v2',
                'area': 'SPb',
                'published_at': '2023-12-02T10:00:00+0300'
            }
        ]

    def test_init(self, db_manager):
        """Тест инициализации DatabaseManager"""
        assert db_manager.config == DB_CONFIG
        assert db_manager.conn is None
        assert db_manager.cur is None

    def test_connect_success(self, db_manager, monkeypatch):
        """Тест успешного подключения к БД"""

        # Мокаем psycopg2.connect чтобы не подключаться к реальной БД
        class MockConnection:
            def set_client_encoding(self, encoding):
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

    def test_connect_failure(self, db_manager, monkeypatch):
        """Тест неудачного подключения к БД"""

        def mock_connect(**kwargs):
            raise psycopg2.OperationalError("Connection failed")

        monkeypatch.setattr('psycopg2.connect', mock_connect)

        result = db_manager.connect()
        assert result is False

    def test_create_tables_success(self, db_manager, monkeypatch):
        """Тест успешного создания таблиц"""
        executed_queries = []

        class MockCursor:
            def execute(self, query):
                executed_queries.append(query)

            def close(self):
                pass

        class MockConnection:
            def cursor(self):
                return MockCursor()

            def commit(self):
                pass

            def close(self):
                pass

        monkeypatch.setattr('psycopg2.connect', lambda **kwargs: MockConnection())
        db_manager.connect()

        result = db_manager.create_tables()

        assert result is True
        assert len(executed_queries) == 2
        assert "CREATE TABLE IF NOT EXISTS employers" in executed_queries[0]
        assert "CREATE TABLE IF NOT EXISTS vacancies" in executed_queries[1]

    def test_insert_employer_success(self, db_manager, test_employers, monkeypatch):
        """Тест успешного добавления работодателя"""
        executed_queries = []
        executed_params = []

        class MockCursor:
            def execute(self, query, params=None):
                executed_queries.append(query)
                executed_params.append(params)

        class MockConnection:
            def cursor(self):
                return MockCursor()

            def commit(self):
                pass

        monkeypatch.setattr('psycopg2.connect', lambda **kwargs: MockConnection())
        db_manager.connect()

        employer = test_employers[0]
        result = db_manager.insert_employer(employer)

        assert result is True
        assert "INSERT INTO employers" in executed_queries[0]
        assert executed_params[0][0] == employer['id']
        assert executed_params[0][1] == employer['name']

    def test_insert_vacancy_success(self, db_manager, test_vacancies, monkeypatch):
        """Тест успешного добавления вакансии"""
        executed_queries = []
        executed_params = []

        class MockCursor:
            def execute(self, query, params=None):
                executed_queries.append(query)
                executed_params.append(params)

        class MockConnection:
            def cursor(self):
                return MockCursor()

            def commit(self):
                pass

        monkeypatch.setattr('psycopg2.connect', lambda **kwargs: MockConnection())
        db_manager.connect()

        vacancy = test_vacancies[0]
        result = db_manager.insert_vacancy(vacancy)

        assert result is True
        assert "INSERT INTO vacancies" in executed_queries[0]
        assert executed_params[0][0] == vacancy['id']
        assert executed_params[0][1] == vacancy['employer_id']

    def test_fill_database_success(self, db_manager, test_employers, test_vacancies, monkeypatch):
        """Тест успешного заполнения базы данных"""
        insert_counts = {'employers': 0, 'vacancies': 0}

        class MockCursor:
            def execute(self, query, params=None):
                if "INSERT INTO employers" in query:
                    insert_counts['employers'] += 1
                elif "INSERT INTO vacancies" in query:
                    insert_counts['vacancies'] += 1

            def close(self):
                pass

        class MockConnection:
            def cursor(self):
                return MockCursor()

            def commit(self):
                pass

            def close(self):
                pass

        monkeypatch.setattr('psycopg2.connect', lambda **kwargs: MockConnection())
        db_manager.connect()

        result = db_manager.fill_database(test_employers, test_vacancies)

        assert result is True
        assert insert_counts['employers'] == len(test_employers)
        assert insert_counts['vacancies'] == len(test_vacancies)

    def test_clear_tables(self, db_manager, monkeypatch):
        """Тест очистки таблиц"""
        executed_queries = []

        class MockCursor:
            def execute(self, query):
                executed_queries.append(query)

        class MockConnection:
            def cursor(self):
                return MockCursor()

            def commit(self):
                pass

        monkeypatch.setattr('psycopg2.connect', lambda **kwargs: MockConnection())
        db_manager.connect()

        db_manager.clear_tables()

        assert "DELETE FROM vacancies" in executed_queries[0]
        assert "DELETE FROM employers" in executed_queries[1]

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
