"""
Конфигурация для тестов
"""
import pytest
import sys
import os

# Добавляем src в путь для импорта
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.config import DB_CONFIG


@pytest.fixture
def test_db_config():
    """Конфигурация тестовой базы данных"""
    config = DB_CONFIG.copy()
    config['dbname'] = 'test_hh_vacancies'
    return config


@pytest.fixture
def sample_employer_data():
    """Пример данных работодателя"""
    return {
        'id': '12345',
        'name': 'Test Company',
        'description': 'Test description',
        'area': 'Moscow',
        'site_url': 'https://test.com',
        'open_vacancies': 10
    }


@pytest.fixture
def sample_vacancy_data():
    """Пример данных вакансии"""
    return {
        'id': 'vacancy_123',
        'name': 'Python Developer',
        'employer_id': '12345',
        'salary_from': 100000,
        'salary_to': 150000,
        'url': 'https://hh.ru/vacancy/123',
        'area': 'Moscow',
        'published_at': '2023-12-01T10:00:00+0300'
    }


@pytest.fixture
def mock_employer_response():
    """Мок ответа API для работодателя"""
    return {
        "id": "12345",
        "name": "Test Company",
        "description": "<p>Test description</p>",
        "area": {"name": "Moscow"},
        "site_url": "https://test.com",
        "open_vacancies": 10
    }


@pytest.fixture
def mock_vacancies_response():
    """Мок ответа API для вакансий"""
    return {
        "items": [
            {
                "id": "vacancy_123",
                "name": "Python Developer",
                "employer": {"id": "12345"},
                "salary": {"from": 100000, "to": 150000, "currency": "RUR"},
                "alternate_url": "https://hh.ru/vacancy/123",
                "area": {"name": "Moscow"},
                "published_at": "2023-12-01T10:00:00+0300"
            }
        ],
        "pages": 1,
        "page": 0,
        "found": 1
    }
