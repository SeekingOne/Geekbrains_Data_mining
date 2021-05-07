import scrapy
from scrapy.item import Item
import re


class CarData(Item):
    url = scrapy.Field()
    name = scrapy.Field()
    photo_urls = scrapy.Field()
    specs = scrapy.Field()
    description = scrapy.Field()
    seller = scrapy.Field()


class AutoyoulaSpider(scrapy.Spider):
    name = 'autoyoula'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/']

    def _get_follow(self, response, selector, callback):
        for item in response.css(selector):
            url = item.attrib['href']
            yield response.follow(url, callback)

    def parse(self, response, *args, **kwargs):
        yield from self._get_follow(
            response,
            ".TransportMainFilters_brandsList__2tIkv .ColumnItemList_column__5gjdt a.blackLink",
            self.parse_brand
        )

    def parse_brand(self, response):
        # Parse cars
        yield from self._get_follow(
            response,
            ".app_gridContentChildren__17ZMX .SerpSnippet_name__3F7Yu.blackLink",
            self.parse_car
        )

        # Parse pages
        yield from self._get_follow(
            response,
            ".Paginator_block__2XAPy a.Paginator_button__u1e7D",
            self.parse_brand
        )

    def parse_car(self, response):
        data = CarData()
        data["url"] = response.url
        data["name"] = response.css(".AdvertCard_advertTitle__1S1Ak::text").extract_first()
        data["photo_urls"] = self._get_photo_urls(response)
        data["specs"] = self._get_specs(response)
        data["description"] = response.css(
            '.AdvertCard_descriptionInner__KnuRi[data-target="advert-info-descriptionFull"]::text'
        ).extract_first()
        data["seller"] = self.get_author_id(response)

        print(data["name"])
        yield data

    @staticmethod
    def _get_photo_urls(response):
        photo_tags = response.css('.PhotoGallery_thumbnails__3-1Ob .PhotoGallery_thumbnailItem__UmhLO')
        photo_urls = [tag.attrib['style'].split("url(", 1)[1].split(")", 1)[0] for tag in photo_tags]
        return photo_urls

    @staticmethod
    def _get_specs(response):
        spec_labels = list()
        spec_values = list()
        for item in response.css(".AdvertCard_specs__2FEHc .AdvertSpecs_row__ljPcX"):
            spec_labels.append(item.css(".AdvertSpecs_label__2JHnS::text").extract_first())
            spec_values.append(item.css(".AdvertSpecs_data__xK2Qx::text").extract_first()
                               or item.css(".AdvertSpecs_data__xK2Qx a::text").extract_first())

        return dict(zip(spec_labels, spec_values))

    @staticmethod
    def get_author_id(response):
        marker = "window.transitState = decodeURIComponent"
        for script in response.css("script"):
            try:
                if marker in script.css("::text").extract_first():
                    re_pattern = re.compile(r"youlaId%22%2C%22([a-zA-Z|\d]+)%22%2C%22avatar")
                    result = re.findall(re_pattern, script.css("::text").extract_first())
                    return (
                        response.urljoin(f"/user/{result[0]}").replace("auto.", "", 1)
                        if result
                        else None
                    )
            except TypeError:
                pass
