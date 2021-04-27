"""
Источник: https://5ka.ru/special_offers/
Задача организовать сбор данных,
необходимо иметь метод сохранения данных в .json файлы
результат: Данные скачиваются с источника, при вызове метода/функции сохранения в файл скачанные данные сохраняются
в Json файлы. Для каждой категории товаров должен быть создан отдельный файл
и содержать товары исключительно соответсвующие данной категории.
пример структуры данных для файла:
нейминг ключей можно делать отличным от примера

{
"name": "имя категории",
"code": "Код соответсвующий категории (используется в запросах)",
"products": [{PRODUCT}, {PRODUCT}........] # список словарей товаров соответсвующих данной категории
}
"""

import time
import json
from pathlib import Path
import requests


class ParseTheHellOutOfSomething:
    """
    Базовый класс с общими методами обращения к сайту и сохранения данных
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"
    }
    max_calls = 10

    def __init__(self, target_folder: str):
        self.target_path = Path(__file__).parent.joinpath(target_folder)
        if not self.target_path.exists():
            self.target_path.mkdir()

    def _get_response(self, target_url: str, params: dict = None):
        current_call = 1
        while current_call <= self.max_calls:
            response = requests.get(target_url, headers=self.headers, params=params)
            if response.status_code == 200:
                return response
            time.sleep(3)
            current_call += 1
        raise TimeoutError

    def _save(self, data: dict, file_name: str):
        save_path = self.target_path.joinpath(file_name)
        save_path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
        print(f"File created: {file_name}")


class ParseTheHellOutOf5ka(ParseTheHellOutOfSomething):
    """
    Производный класс с методами, специфичными для 5ки
    """

    def __init__(self, products_url, category_url, folder="Products by Category"):
        super().__init__(folder)
        self.products_url = products_url
        self.category_url = category_url

    def _categories(self):
        response = self._get_response(self.category_url)
        response_results: dict = response.json()
        for result in response_results:
            yield result

    def _products(self, category: str = None):
        params = {
            "records_per_page": 20
        }
        page = 1
        next_url = "some next url"
        if category is not None:
            params["categories"] = category

        while next_url:
            # В перезаписи URL на каждой итерации нет необходимости, так как все продукты успешно вычитываются
            # по комбинации стартового URL и номера страницы.
            # "Next" используется только для определения конца данных.
            params["page"] = page
            response = self._get_response(self.products_url, params)
            response_results: dict = response.json()
            next_url = response_results["next"]
            page += 1
            for result in response_results["results"]:
                yield result

    def run(self):
        product_group = {}

        for cat in self._categories():
            product_group["name"] = cat["parent_group_name"]
            product_group["code"] = cat["parent_group_code"]
            product_group["products"] = []

            # print(cat)
            for product in self._products(product_group["code"]):
                product_group["products"].append(product)

            file_name = f"{product_group['code']}.json"
            self._save(product_group, file_name)


if __name__ == "__main__":
    prod_url = "https://5ka.ru/api/v2/special_offers/"
    cat_url = "https://5ka.ru/api/v2/categories/"

    parser = ParseTheHellOutOf5ka(prod_url, cat_url)
    parser.run()
