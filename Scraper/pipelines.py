# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from time import strftime
from Scraper.sif_models import *
from Scraper.settings import SQS
import boto.sqs
from boto.sqs.message import RawMessage
import json


class MySQLStorePipeline(object):
    def __init__(self):
        self.new = {}

    def process_item(self, item, spider):
        filter_id = item['filter_id']
        item_id = item['item_id']
        try:
            Results.get((Results.filter == filter_id) & (Results.item == item_id))
        except Results.DoesNotExist:
            if filter_id not in self.new:
                self.new[filter_id] = {}
                self.new[filter_id] = []
            self.new[filter_id].append(item_id)
            try:
                Results.create(
                    filter=item['filter_id'],
                    price=item['price'],
                    url=item['url'],
                    title=item['title'],
                    added_on=strftime("%Y-%m-%d %H:%M:%S"),
                    details=item['details'],
                    item=item['item_id']
                )
            except Exception as e:
                print e.message

        return item

    def close_spider(self, spider):
        conn = boto.sqs.connect_to_region(
            SQS['region'],
            aws_access_key_id=SQS['key'],
            aws_secret_access_key=SQS['secret']
        )
        queue = conn.get_queue('email')
        for filter in self.new:
            user = self.get_user(filter)
            msg = RawMessage()
            msg.set_body(json.dumps({
                'subject': 'Nauji ' + spider.name + ' skelbimai',
                'email': user.email,
                'template': 'results',
                'data': {'filter': filter, 'results': self.new[filter]}
            }))
            queue.write(msg)

    def get_user(self, filter):
        return Filter.get(Filter.id == filter).user