"""
Главный модуль приложения
"""
from hh_api import HeadHunterAPI
from database import DatabaseManager
from db_manager import DBManager


def main():
    """Основная функция приложения"""
    print("=" * 50)
    print("ПАРСЕР ВАКАНСИЙ С HH.RU")
    print("=" * 50)

    # Инициализация
    hh_api = HeadHunterAPI()
    db_manager = DatabaseManager()

    # Подключаемся к БД
    if not db_manager.connect():
        return

    # Создаем таблицы
    if not db_manager.create_tables():
        return

    # Очищаем таблицы
    db_manager.clear_tables()

    # Получаем данные
    employers = hh_api.get_employers()
    vacancies = hh_api.get_vacancies()

    # Заполняем БД
    if employers and vacancies:
        db_manager.fill_database(employers, vacancies)

    # Закрываем соединение
    db_manager.close()

    # Запускаем интерфейс запросов
    run_query_interface()


def run_query_interface():
    """Интерфейс для выполнения запросов"""
    manager = DBManager()

    if not manager.connect():
        return

    while True:
        print("\n" + "=" * 50)
        print("ВЫБЕРИТЕ ДЕЙСТВИЕ:")
        print("1. Компании и количество вакансий")
        print("2. Все вакансии")
        print("3. Средняя зарплата")
        print("4. Вакансии с зарплатой выше средней")
        print("5. Поиск вакансий по ключевому слову")
        print("0. Выход")

        choice = input("\nВаш выбор: ").strip()

        if choice == '1':
            show_companies_vacancies_count(manager)
        elif choice == '2':
            show_all_vacancies(manager)
        elif choice == '3':
            show_avg_salary(manager)
        elif choice == '4':
            show_higher_salary_vacancies(manager)
        elif choice == '5':
            search_vacancies(manager)
        elif choice == '0':
            break
        else:
            print("Неверный выбор")

    manager.close()
    print("\nПрограмма завершена!")


def show_companies_vacancies_count(manager):
    """Показывает компании и количество вакансий"""
    print("\n--- КОМПАНИИ И КОЛИЧЕСТВО ВАКАНСИЙ ---")
    results = manager.get_companies_and_vacancies_count()
    for company, count in results:
        print(f"{company}: {count} вакансий")


def show_all_vacancies(manager):
    """Показывает все вакансии"""
    print("\n--- ВСЕ ВАКАНСИИ ---")
    results = manager.get_all_vacancies()
    for company, vacancy, salary_from, salary_to, url in results[:10]:  # Показываем первые 10
        salary = format_salary(salary_from, salary_to)
        print(f"{company}")
        print(f"   {vacancy}")
        print(f"   {salary}")
        print(f"   {url}\n")


def show_avg_salary(manager):
    """Показывает среднюю зарплату"""
    print("\n--- СРЕДНЯЯ ЗАРПЛАТА ---")
    avg_salary = manager.get_avg_salary()
    print(f"Средняя зарплата: {avg_salary:,.0f} руб.".replace(',', ' '))


def show_higher_salary_vacancies(manager):
    """Показывает вакансии с зарплатой выше средней"""
    print("\n--- ВАКАНСИИ С ЗАРПЛАТОЙ ВЫШЕ СРЕДНЕЙ ---")
    results = manager.get_vacancies_with_higher_salary()
    for company, vacancy, salary_from, salary_to, url in results:
        salary = format_salary(salary_from, salary_to)
        print(f"{company} - {vacancy}")
        print(f"   {salary}")
        print(f"   {url}\n")


def search_vacancies(manager):
    """Ищет вакансии по ключевому слову"""
    keyword = input("Введите ключевое слово для поиска: ").strip()
    if not keyword:
        print("Ключевое слово не может быть пустым")
        return

    print(f"\n--- РЕЗУЛЬТАТЫ ПОИСКА ПО '{keyword.upper()}' ---")
    results = manager.get_vacancies_with_keyword(keyword)

    if results:
        for company, vacancy, salary_from, salary_to, url in results:
            salary = format_salary(salary_from, salary_to)
            print(f"{company} - {vacancy}")
            print(f"   {salary}")
            print(f"   {url}\n")
    else:
        print("Вакансии не найдены")


def format_salary(salary_from, salary_to):
    """Форматирует зарплату для отображения"""
    if salary_from and salary_to:
        return f"{salary_from:,} - {salary_to:,} руб.".replace(',', ' ')
    elif salary_from:
        return f"от {salary_from:,} руб.".replace(',', ' ')
    elif salary_to:
        return f"до {salary_to:,} руб.".replace(',', ' ')
    else:
        return "не указана"


if __name__ == '__main__':
    main()
