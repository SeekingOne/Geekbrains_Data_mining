# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymongo


class MongoPipeline:

    def __init__(self, empl_collection_name, vac_collection_name, mongo_db):

        self.client = pymongo.MongoClient()
        self.collections = {
            "VacancyData": self.client[mongo_db][vac_collection_name],
            "EmployerData": self.client[mongo_db][empl_collection_name],
        }

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_db=crawler.settings.get('MONGO_DB'),
            empl_collection_name=crawler.settings.get('MONGO_COLLECTION_EMPLOYER'),
            vac_collection_name=crawler.settings.get('MONGO_COLLECTION_VACANCY'),
        )

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        item_class = item.__class__.__name__
        self.collections[item_class].insert_one(ItemAdapter(item).asdict())
        return item
