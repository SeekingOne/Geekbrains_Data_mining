import scrapy
from . import xpath as xp
from ..Loaders import AvitoApartmentLoader
from ..items import ApartmentData


class AvitoSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['avito.ru']
    start_urls = ['https://www.avito.ru/korolev/kvartiry/prodam']

    def _get_follow(self, response, selector_str, callback):
        for item in response.xpath(xp.page_selectors[selector_str]):
            yield response.follow(item, callback=callback)

    def parse(self, response, *args, **kwargs):
        yield from self._get_follow(response, "pages", self.parse)
        yield from self._get_follow(response, "apartments", self.parse_apt)

    def parse_apt(self, response):
        apt_load = AvitoApartmentLoader(item=ApartmentData(), response=response)
        apt_load.add_value("url", response.url)
        for fld, path in xp.apartment_selectors.items():
            apt_load.add_xpath(fld, path)
        apt = apt_load.load_item()
        yield apt

