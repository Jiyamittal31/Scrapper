# In pipelines.py

import pymongo
from itemadapter import ItemAdapter

class MongoPipeline:
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.client = None
        self.db = None

    @classmethod
    def from_crawler(cls, crawler):
        # This method gets the settings from the crawler
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )

    def open_spider(self, spider):
        # Connect to the MongoDB server
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        spider.logger.info("Successfully connected to MongoDB.")
        # Define the collection for this spider
        self.collection = self.db[spider.name]

    def close_spider(self, spider):
        # Close the connection
        self.client.close()
        spider.logger.info("MongoDB connection closed.")

    def process_item(self, item, spider):
        # Convert the Scrapy item to a dictionary
        item_dict = ItemAdapter(item).asdict()
        
        # Use the 'cin' as the unique identifier to find and update the document.
        # The 'upsert=True' option creates a new document if one doesn't exist.
        self.collection.update_one(
            {'cin': item_dict['cin']},
            {'$set': item_dict},
            upsert=True
        )
        spider.logger.info(f"Saved item to MongoDB: {item_dict['cin']}")
        return item
