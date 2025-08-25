import scrapy

class McascraperItem(scrapy.Item):
    # This class defines the fields for your item. It's like a schema for your data.
    # We define a field for each piece of data we want to collect.
    cin = scrapy.Field()
    company_name = scrapy.Field()
    roc_code = scrapy.Field()
    registration_number = scrapy.Field()
    company_category = scrapy.Field()
    company_sub_category = scrapy.Field()
    class_of_company = scrapy.Field()
    date_of_incorporation = scrapy.Field()
    age_of_company = scrapy.Field()
    activity = scrapy.Field()
    number_of_members = scrapy.Field()
