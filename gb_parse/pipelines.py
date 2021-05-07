# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymongo


class MongoPipeline:

    def __init__(self, collection_name, mongo_db):
        self.collection_name = collection_name
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            # mongo_uri=crawler.settings.get('MONGO_URI'),
            # mongo_db=crawler.settings.get('MONGO_DB', 'items')
            mongo_db=crawler.settings.get('MONGO_DB'),
            collection_name=crawler.settings.get('MONGO_COLLECTION')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient()
        self.collection = self.client[self.mongo_db][self.collection_name]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.collection.insert_one(ItemAdapter(item).asdict())
        return item
