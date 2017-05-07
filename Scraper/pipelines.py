# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from time import strftime
from Scraper.sif_models import *
import logging

logging.basicConfig(filename='pipeline.log',level=logging.DEBUG,)

class ScraperPipeline(object):
    def process_item(self, item, spider):
        return item


class MySQLStorePipeline(object):
    def process_item(self, item, spider):
        try:
            result = Results.get(
                (Results.filter == item['filter_id']) & (Results.item == item['item_id'])
            )
            result.is_new = 0
            result.save()
        except Results.DoesNotExist:
            try:
                Results.create(
                    filter=item['filter_id'],
                    is_new=1,
                    price=item['price'],
                    url=item['url'],
                    title=item['title'],
                    added_on=strftime("%Y-%m-%d %H:%M:%S"),
                    details=item['details'],
                    item=item['item_id']
                )
            except Exception as e:
                logging.error(e.message)
                print e.message

        return item
