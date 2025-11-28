"""
Модуль для работы с API HeadHunter
"""
import requests
import time
from config import HH_API_URL, EMPLOYER_IDS


class HeadHunterAPI:
    """Класс для работы с API HeadHunter"""

    def __init__(self):
        self.url = HH_API_URL

    def get_employers(self):
        """Получает данные о работодателях"""
        print("Получение данных о компаниях...")
        employers = []

        for employer_id in EMPLOYER_IDS:
            try:
                response = requests.get(f'{self.url}employers/{employer_id}',
                                        timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    employer = {
                        'id': data['id'],
                        'name': data['name'],
                        'description': self.clean_text(data.get('description', '')),
                        'area': data['area']['name'],
                        'site_url': data.get('site_url', ''),
                        'open_vacancies': data['open_vacancies']
                    }
                    employers.append(employer)
                    print(f"Получены данные: {data['name']}")
                else:
                    print(f"Ошибка для компании {employer_id}: {response.status_code}")

                time.sleep(0.1)  # Задержка между запросами

            except Exception as e:
                print(f"Ошибка при получении компании {employer_id}: {e}")

        print(f"Получено {len(employers)} компаний")
        return employers

    def get_vacancies(self):
        """Получает все вакансии для выбранных компаний"""
        print("Получение вакансий...")
        all_vacancies = []

        for employer_id in EMPLOYER_IDS:
            try:
                vacancies = []
                page = 0
                pages = 1

                while page < pages:
                    params = {
                        'employer_id': employer_id,
                        'per_page': 100,
                        'page': page,
                        'only_with_salary': True
                    }

                    response = requests.get(f'{self.url}vacancies',
                                            params=params, timeout=10)

                    if response.status_code == 200:
                        data = response.json()
                        pages = data['pages']

                        for item in data['items']:
                            vacancy = {
                                'id': item['id'],
                                'name': item['name'],
                                'employer_id': employer_id,
                                'salary_from': item['salary'].get('from'),
                                'salary_to': item['salary'].get('to'),
                                'url': item['alternate_url'],
                                'area': item['area']['name'],
                                'published_at': item['published_at']
                            }
                            vacancies.append(vacancy)

                        page += 1
                        time.sleep(0.1)  # Задержка между страницами
                    else:
                        print(f"Ошибка при получении вакансий: {response.status_code}")
                        break

                all_vacancies.extend(vacancies)
                print(f"Компания {employer_id}: {len(vacancies)} вакансий")

            except Exception as e:
                print(f"Ошибка при получении вакансий для компании {employer_id}: {e}")

        print(f"Всего получено {len(all_vacancies)} вакансий")
        return all_vacancies

    def clean_text(self, text):
        """Очищает текст от HTML тегов"""
        if not text:
            return ""
        import re
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text)[:500]  # Ограничиваем длину
