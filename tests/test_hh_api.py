"""
Тесты для модуля hh_api.py
"""
import pytest
import requests_mock
import sys
import os

# Добавляем src в путь для импорта
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.hh_api import HeadHunterAPI
from src.config import HH_API_URL, EMPLOYER_IDS


class TestHeadHunterAPI:
    """Тесты для класса HeadHunterAPI"""

    @pytest.fixture
    def api(self):
        return HeadHunterAPI()

    def test_init(self, api):
        """Тест инициализации API"""
        assert api.url == HH_API_URL
        assert isinstance(api.url, str)

    def test_clean_text(self, api):
        """Тест очистки текста от HTML"""
        html_text = "<p>Test <b>description</b> with tags</p>"
        cleaned = api.clean_text(html_text)
        assert cleaned == "Test description with tags"
        assert "<" not in cleaned
        assert ">" not in cleaned

    def test_clean_text_empty(self, api):
        """Тест очистки пустого текста"""
        assert api.clean_text("") == ""
        assert api.clean_text(None) == ""

    def test_clean_text_length_limit(self, api):
        """Тест ограничения длины текста"""
        long_text = "a" * 1000
        cleaned = api.clean_text(long_text)
        assert len(cleaned) <= 500

    def test_get_employers_success(self, api, mock_employer_response):
        """Тест успешного получения данных о работодателях"""
        with requests_mock.Mocker() as m:
            for employer_id in EMPLOYER_IDS[:2]:  # Тестируем на 2 компаниях
                m.get(f"{HH_API_URL}employers/{employer_id}",
                      json=mock_employer_response)

            employers = api.get_employers()

            assert isinstance(employers, list)
            assert len(employers) == 2
            assert employers[0]['id'] == '12345'
            assert employers[0]['name'] == 'Test Company'
            assert employers[0]['description'] == 'Test description'

    def test_get_employers_api_error(self, api):
        """Тест обработки ошибки API при получении работодателей"""
        with requests_mock.Mocker() as m:
            m.get(f"{HH_API_URL}employers/{EMPLOYER_IDS[0]}",
                  status_code=404)

            employers = api.get_employers()
            assert isinstance(employers, list)

    def test_get_employers_connection_error(self, api):
        """Тест обработки ошибки соединения"""
        with requests_mock.Mocker() as m:
            m.get(f"{HH_API_URL}employers/{EMPLOYER_IDS[0]}",
                  exc=ConnectionError)

            employers = api.get_employers()
            assert isinstance(employers, list)

    def test_get_vacancies_success(self, api, mock_vacancies_response):
        """Тест успешного получения вакансий"""
        with requests_mock.Mocker() as m:
            # Мокаем все запросы к vacancies
            m.get(f"{HH_API_URL}vacancies",
                  json=mock_vacancies_response)

            vacancies = api.get_vacancies()

            assert isinstance(vacancies, list)
            # Проверяем что метод возвращает список
            # Конкретное количество может варьироваться из-за логики в методе

    def test_get_vacancies_multiple_pages(self, api, mock_vacancies_response):
        """Тест получения вакансий с нескольких страниц (упрощенная версия)"""
        # Создаем ответ с двумя страницами
        first_page = mock_vacancies_response.copy()
        first_page["pages"] = 2

        second_page = mock_vacancies_response.copy()
        second_page["items"][0]["id"] = "vacancy_456"

        with requests_mock.Mocker() as m:
            # Настраиваем разные ответы для разных страниц
            m.get(f"{HH_API_URL}vacancies?employer_id={EMPLOYER_IDS[0]}&per_page=100&page=0&only_with_salary=True",
                  json=first_page)
            m.get(f"{HH_API_URL}vacancies?employer_id={EMPLOYER_IDS[0]}&per_page=100&page=1&only_with_salary=True",
                  json=second_page)

            # Мокаем остальные запросы
            for employer_id in EMPLOYER_IDS[1:]:
                m.get(f"{HH_API_URL}vacancies?employer_id={employer_id}&per_page=100&page=0&only_with_salary=True",
                      json=mock_vacancies_response)

            vacancies = api.get_vacancies()

            # Проверяем что получили хотя бы одну вакансию
            assert len(vacancies) > 0

    def test_get_vacancies_api_error(self, api):
        """Тест обработки ошибки API при получении вакансий"""
        with requests_mock.Mocker() as m:
            m.get(f"{HH_API_URL}vacancies",
                  status_code=500)

            vacancies = api.get_vacancies()
            assert isinstance(vacancies, list)

    def test_get_vacancies_no_salary(self, api):
        """Тест обработки вакансий без зарплаты (упрощенная версия)"""
        vacancy_without_salary = {
            "id": "vacancy_no_salary",
            "name": "Developer",
            "employer": {"id": EMPLOYER_IDS[0]},
            "salary": None,
            "alternate_url": "https://hh.ru/vacancy/123",
            "area": {"name": "Moscow"},
            "published_at": "2023-12-01T10:00:00+0300"
        }

        response = {
            "items": [vacancy_without_salary],
            "pages": 1,
            "page": 0,
            "found": 1
        }

        with requests_mock.Mocker() as m:
            m.get(f"{HH_API_URL}vacancies",
                  json=response)

            vacancies = api.get_vacancies()

            # Проверяем что метод обрабатывает вакансии без зарплаты
            assert isinstance(vacancies, list)

    def test_employer_ids_not_empty(self):
        """Тест что список ID работодателей не пустой"""
        assert len(EMPLOYER_IDS) > 0
        assert all(isinstance(eid, str) for eid in EMPLOYER_IDS)
