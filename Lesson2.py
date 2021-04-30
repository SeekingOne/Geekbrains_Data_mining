"""
Источник https://gb.ru/posts/
Необходимо обойти все записи в блоге и извлечь из них информацию следующих полей:
url страницы материала
Заголовок материала
Первое изображение материала (Ссылка)
Дата публикации (в формате datetime)
имя автора материала
ссылка на страницу автора материала
комментарии в виде (автор комментария и текст комментария)

Структуру сохраняем в MongoDB
"""

from pymongo import MongoClient
from urllib.parse import urljoin
import requests
import bs4
import time
import datetime as dt


class ConnectionTimeout(Exception):
    def __init__(self, url: str):
        super().__init__(f'Исполнение прервано: страница блога GeekBrains "{url}" не отвечает')


class ParseTheHellOutOfGbBlog:
    """
    В классе исплользован простой алгоритм последовательного обхода страниц блога
    по ссылкам, извлекаемым из кнопки "Next"
    """
    max_calls = 50  # Допустимый максимум попыток обращения к URL

    def __init__(self, start_url, collection=None):
        self.time = time.time()
        self.start_url = start_url
        self.collection = collection
        self.processed_post_urls = set()
        self.processed_pages = 0
        self.processed_posts = 0

    def _get_response(self, url, *args, **kwargs):
        current_call = 1
        if self.time + 0.9 < time.time():
            time.sleep(0.5)
        while current_call <= self.max_calls:
            response = requests.get(url, *args, **kwargs)
            if response.status_code == 200:
                self.time = time.time()
                return response
            time.sleep(3)
            current_call += 1
        # Число обращений превышено - выводим промежуточные результаты и выдаем ошибку
        print(f"Обработано страниц: {self.processed_pages}")
        print(f"Обработано постов: {self.processed_posts}")
        raise ConnectionTimeout(url)

    def _get_soup(self, url, *args, **kwargs):
        soup = bs4.BeautifulSoup(self._get_response(url, *args, **kwargs).text, "lxml")
        return soup

    def _process_page(self, url):
        print("Processing page: ", url)
        page_data = self._parse_page(url)

        for post_url in page_data['post_urls']:
            if post_url not in self.processed_post_urls:
                post_data = self._parse_post(post_url)
                self._save(post_data)
                self.processed_post_urls.add(post_url)
                self.processed_posts += 1
        self.processed_pages += 1
        return page_data['next_page']

    def _get_next_page(self, paginator: bs4.Tag):
        # Достаем ссылку на следующую страницу из кнопки "Next"
        li_tags = paginator.find_all('li', attrs={"class": "page"})
        next_page_tag = None
        for li_tag in li_tags:
            next_page_tag = li_tag.find('a', attrs={"rel": "next"})
            if next_page_tag is not None:
                break
        if next_page_tag is not None:
            return urljoin(self.start_url, next_page_tag.attrs.get("href"))
        else:
            return None

    def _parse_page(self, url):
        soup = self._get_soup(url)

        page_data = {
            "post_urls": set(
                urljoin(self.start_url, post_partial_url) for post_partial_url in
                set(post.find('a').attrs.get('href') for post in
                    soup.find_all('div', attrs={"class": "post-item event"}))
            ),
            "next_page": self._get_next_page(soup.find('ul', attrs={"class": "gb__pagination"}))
        }
        return page_data

    def _parse_post(self, url):
        print("Post: ", url)
        soup = self._get_soup(url)
        post_datetime = soup.find("time", attrs={"class": "text-md text-muted m-r-md"}).get("datetime")
        content = soup.find('div', attrs={"class": "blogpost-content"})
        img = content.find('img', attrs={"alt": ""})
        author_tag = soup.find("div", attrs={"itemprop": "author"})
        post_id = soup.find("comments").attrs.get("commentable-id")

        data = {
            "post": {
                "id": post_id,
                "url": url,
                "title": soup.find('h1').text,
                "image_url": img.attrs.get("src"),
                "date": dt.datetime.fromtimestamp(int(time.mktime(
                    time.strptime(post_datetime, "%Y-%m-%dT%X%z"))) + time.timezone)
            },
            "author": {
                "name": author_tag.text,
                "url": urljoin(url, author_tag.parent.attrs.get("href")),
            },
            "comments": self._get_comments(post_id)
        }

        return data

    def _get_comments(self, post_id):
        api_path = f"/api/v2/comments?commentable_type=Post&commentable_id={post_id}&order=desc"
        response = self._get_response(urljoin(self.start_url, api_path))
        data: list = response.json()

        return self._parse_comments(data)

    def _parse_comments(self, raw_comments: list):
        clean_comments = []
        for raw_comment in raw_comments:
            comment = {
                "author": raw_comment["comment"]["user"]["full_name"],
                "text": raw_comment["comment"]["body"],
                "likes": raw_comment["comment"]["likes_count"],
                "replies": self._parse_comments(raw_comment["comment"]["children"])
            }
            clean_comments.append(comment)
        return clean_comments

    def _save(self, data: dict):
        self.collection.insert_one(data)

    def run(self):
        next_page = self._process_page(self.start_url)

        while next_page:
            next_page = self._process_page(next_page)
        print(f"Обработано страниц: {self.processed_pages}")
        print(f"Обработано постов: {self.processed_posts}")


if __name__ == '__main__':
    mongo_collection = MongoClient()["parse_gb_homework"]["gb_blog00"]
    parser = ParseTheHellOutOfGbBlog('https://gb.ru/posts', mongo_collection)
    parser.run()
