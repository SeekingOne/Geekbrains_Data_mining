"""
Продолжить работу с парсером блога GB
Реализовать SQL базу данных посредствам SQLAlchemy
Реализовать реалиционные связи между Постом и Автором, Постом и Тегом,
Постом и комментарием, Комментарием и комментарием
"""

from urllib.parse import urljoin
import requests
import bs4
import time
import datetime as dt
from Database.Database import Database


class ConnectionTimeout(Exception):
    def __init__(self, url: str):
        super().__init__(f'Страница блога GeekBrains "{url}" не отвечает. Пропускаем...')


class ParseTheHellOutOfGbBlog:
    """
    В классе исплользован простой алгоритм последовательного обхода страниц блога
    по ссылкам, извлекаемым из кнопки "Next"
    """
    max_calls = 10  # Допустимый максимум попыток обращения к URL

    def __init__(self, start_url, db: Database):
        self.time = time.time()
        self.start_url = start_url
        self.db = db
        self.processed_post_urls = set()
        self.bad_urls = set()
        self.processed_pages = 0
        self.processed_posts = 0
        self.bad_urls_count = 0

    def _log_error(self, err: ConnectionTimeout, url: str):
        print(err)
        self.bad_urls.add(url)
        self.bad_urls_count += 1

    def _get_response(self, url, *args, **kwargs):
        current_call = 1
        if self.time + 0.9 < time.time():
            time.sleep(0.5)
        while current_call <= self.max_calls:
            response = requests.get(url, *args, **kwargs)
            if response.status_code % 200 < 100:
                self.time = time.time()
                return response
            time.sleep(3)
            current_call += 1
        # Число обращений превышено - выдаем ошибку
        raise ConnectionTimeout(url)

    def _get_soup(self, url, *args, **kwargs):
        soup = bs4.BeautifulSoup(self._get_response(url, *args, **kwargs).text, "lxml")
        return soup

    def _process_page(self, url):
        print("\nProcessing page: ", url)
        page_data = self._parse_page(url)

        for post_url in page_data['post_urls']:
            if post_url not in self.processed_post_urls:
                post_data = self._parse_post(post_url)
                if post_data:
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
        try:
            soup = self._get_soup(url)
        except ConnectionTimeout as err:
            self._log_error(err, url)
            return {
                "post_urls": [],
                "next_page": None
            }

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
        print("\nGetting post: ", url)
        try:
            soup = self._get_soup(url)
        except ConnectionTimeout as err:
            self._log_error(err, url)
            return None

        # Дата поста
        post_datetime = soup.find("time", attrs={"class": "text-md text-muted m-r-md"}).get("datetime")
        # Ссылка на рисунок
        content = soup.find('div', attrs={"class": "blogpost-content"})
        img_tags = content.findAll(lambda tag: tag.name == 'img' and tag.attrs.get('alt') is not None)
        if len(img_tags) > 0:
            img_url = img_tags[0].attrs.get("src")
        else:
            img_url = ""
        # Автор и id поста
        author_tag = soup.find("div", attrs={"itemprop": "author"})
        post_id = soup.find("comments").attrs.get("commentable-id")

        data = {
            "post": {
                "url": url,
                "title": soup.find('h1').text,
                "image_url": img_url,
                "date": dt.datetime.fromtimestamp(int(time.mktime(
                    time.strptime(post_datetime, "%Y-%m-%dT%X%z"))) + time.timezone)
            },
            "author": {
                "name": author_tag.text,
                "url": urljoin(url, author_tag.parent.attrs.get("href")),
            },
            "tags": [
                {"name": tag.text, "url": urljoin(url, tag.attrs.get("href"))}
                for tag in soup.find_all("a", attrs={"class": "small"})
            ],
            "comments": self._get_comments(url, post_id)
        }

        return data

    def _get_comments(self, url, post_id):
        api_path = f"/api/v2/comments?commentable_type=Post&commentable_id={post_id}"
        try:
            response = self._get_response(urljoin(url, api_path))
        except ConnectionTimeout as err:
            self._log_error(err, urljoin(url, api_path))
            return []

        data: list = response.json()

        return self._parse_comments(data)

    def _parse_comments(self, raw_comments: list):
        clean_comments = []
        for raw_comment in raw_comments:
            comment = {
                "comment_id": raw_comment["comment"]["id"],
                "parent_id": raw_comment["comment"]["parent_id"],
                "author": raw_comment["comment"]["user"]["full_name"],
                "text": raw_comment["comment"]["body"],
                "likes": raw_comment["comment"]["likes_count"],
                "replies": self._parse_comments(raw_comment["comment"]["children"])
            }
            clean_comments.append(comment)
        return clean_comments

    def _save(self, data: dict):
        self.db.add_post(data)
        self.db.check_data(data)

    def run(self):
        next_page = self._process_page(self.start_url)

        while next_page and self.processed_pages <= 5:
            next_page = self._process_page(next_page)
        print(f"\nПарсинг завершен. \nОбработано страниц: {self.processed_pages}")
        print(f"Обработано постов: {self.processed_posts}")
        print(f"Пропущено нерабочих ссылок: {self.bad_urls_count}")
        if self.bad_urls_count > 0:
            print("Нерабочие ссылки:")
            for url in self.bad_urls:
                print(f" {url}")


if __name__ == '__main__':
    db = Database("sqlite:///gb_blog.db")
    # parser = ParseTheHellOutOfGbBlog('https://gb.ru/posts?page=4', db)
    parser = ParseTheHellOutOfGbBlog('https://gb.ru/posts', db)
    parser.run()
