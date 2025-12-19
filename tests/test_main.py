"""
Тесты для модуля main.py
"""
import pytest
import builtins
import sys
import os

# Добавляем src в путь для импорта
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from unittest.mock import Mock, patch
from src.main import format_salary, show_companies_vacancies_count, show_all_vacancies


class TestMainFunctions:
    """Тесты для функций главного модуля"""

    def test_format_salary_both_values(self):
        """Тест форматирования зарплаты с обеими значениями"""
        result = format_salary(100000, 150000)
        assert result == "100 000 - 150 000 руб."

    def test_format_salary_only_from(self):
        """Тест форматирования зарплаты только с 'от'"""
        result = format_salary(100000, None)
        assert result == "от 100 000 руб."

    def test_format_salary_only_to(self):
        """Тест форматирования зарплаты только с 'до'"""
        result = format_salary(None, 150000)
        assert result == "до 150 000 руб."

    def test_format_salary_no_values(self):
        """Тест форматирования зарплаты без значений"""
        result = format_salary(None, None)
        assert result == "не указана"

    def test_show_companies_vacancies_count(self, monkeypatch):
        """Тест отображения компаний и количества вакансий"""
        mock_manager = Mock()
        mock_manager.get_companies_and_vacancies_count.return_value = [
            ('Company A', 10),
            ('Company B', 5)
        ]

        # Перехватываем вывод print
        printed_lines = []
        monkeypatch.setattr(builtins, 'print', lambda x: printed_lines.append(str(x)))

        show_companies_vacancies_count(mock_manager)

        assert len(printed_lines) > 0
        assert any('Company A' in line for line in printed_lines)
        assert any('Company B' in line for line in printed_lines)
        assert any('10' in line for line in printed_lines)

    def test_show_all_vacancies(self, monkeypatch):
        """Тест отображения всех вакансий"""
        mock_manager = Mock()
        mock_manager.get_all_vacancies.return_value = [
            ('Company A', 'Python Developer', 100000, 150000, 'url1'),
            ('Company B', 'Java Developer', 120000, None, 'url2')
        ]

        printed_lines = []
        monkeypatch.setattr(builtins, 'print', lambda x: printed_lines.append(str(x)))

        show_all_vacancies(mock_manager)

        assert len(printed_lines) > 0
        assert any('Python Developer' in line for line in printed_lines)
        assert any('Java Developer' in line for line in printed_lines)
        assert any('100 000 - 150 000' in line for line in printed_lines)

    @patch('src.main.HeadHunterAPI')
    @patch('src.main.DatabaseManager')
    def test_main_function_structure(self, mock_db_manager, mock_hh_api, monkeypatch):
        """Тест структуры главной функции"""
        # Мокаем все внешние зависимости
        mock_db_instance = Mock()
        mock_db_instance.connect.return_value = True
        mock_db_instance.create_tables.return_value = True
        mock_db_instance.fill_database.return_value = True
        mock_db_manager.return_value = mock_db_instance

        mock_api_instance = Mock()
        mock_api_instance.get_employers.return_value = [{'id': '1', 'name': 'Test'}]
        mock_api_instance.get_vacancies.return_value = [{'id': 'v1', 'name': 'Test Vacancy'}]
        mock_hh_api.return_value = mock_api_instance

        # Мокаем run_query_interface чтобы не запускать интерактивную часть
        mock_interface = Mock()
        monkeypatch.setattr('src.main.run_query_interface', mock_interface)

        # Импортируем и запускаем main
        from src.main import main

        # Заменяем sys.exit на Mock
        with patch('sys.exit') as mock_exit:
            result = main()

        # Проверяем что функции были вызваны
        assert mock_db_instance.connect.called
        assert mock_db_instance.create_tables.called
        assert mock_api_instance.get_employers.called
        assert mock_api_instance.get_vacancies.called
        assert mock_db_instance.fill_database.called
        assert mock_interface.called
