# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class ApartmentData(Item):
    url = Field()
    title = Field()
    price = Field()
    address = Field()
    properties = Field()
    author_url = Field()
