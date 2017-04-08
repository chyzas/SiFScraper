# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class ScraperItem(Item):
    title = Field()
    url = Field()
    price = Field()
    filter_id = Field()
    details = Field()
    item_id = Field()

