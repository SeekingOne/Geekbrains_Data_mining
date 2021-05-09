import scrapy
from . import xpath as xp
from ..Loaders import HHVacancyLoader, HHEmployerLoader, VacancyData, EmployerData


class HHunterSpider(scrapy.Spider):
    name = 'hhunter'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113']

    def _get_follow(self, response, selector_str, callback):
        for item in response.xpath(xp.page_selectors[selector_str]):
            yield response.follow(item, callback=callback)

    def parse(self, response, *args, **kwargs):
        yield from self._get_follow(response, "pages", self.parse_page)

    def parse_page(self, response):
        yield from self._get_follow(response, "pages", self.parse_page)
        yield from self._get_follow(response, "employers", self.parse_employer)
        yield from self._get_follow(response, "vacancies", self.parse_vacancy)

    def parse_vacancy(self, response):
        vcy_load = HHVacancyLoader(item=VacancyData(), response=response, url=response.url)
        vcy_load.add_value("url", response.url)
        for fld, path in xp.vacancy_selectors.items():
            vcy_load.add_xpath(fld, path)
        vcy = vcy_load.load_item()
        yield vcy

    def parse_employer(self, response):
        yield from self._get_follow(response, "employer_vacancies", self.parse_page)

        empl_load = HHEmployerLoader(item=EmployerData(), response=response)
        for fld, path in xp.employer_selectors.items():
            empl_load.add_xpath(fld, path)
        empl = empl_load.load_item()
        yield empl
