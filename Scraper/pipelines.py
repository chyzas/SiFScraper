# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import boto3
import json
from Scraper.sif_models import *
from Scraper.settings import SQS


class MySQLStorePipeline(object):
    def __init__(self):
        self.all = {}

    def process_item(self, item, spider):
        try:
            filter_id = item['filter_id']
            if filter_id not in self.all:
                self.all[filter_id] = {}
                self.all[filter_id] = []
            self.all[filter_id].append(item)
        except Exception as e:
            print(e)

        return item

    def get_data_source(self, results):
        data = []
        for item in results:
            row = {
                'filter': item['filter_id'],
                'price': item['price'],
                'url': item['url'],
                'title': item['title'],
                'details': item['details'],
                'ads_id': item['ads_id'],
                'image': item['image']
            }
            data.append(row)
        return data

    def close_spider(self, spider):
        for filter_id in self.all:
            scrapy_results = self.all[filter_id]
            scrapy_ads_ids = [i['ads_id'] for i in scrapy_results]
            results = Results.select().where((Results.filter == filter_id) & (Results.ads_id << scrapy_ads_ids))
            if len(results) == 0:
                data_source = self.get_data_source(scrapy_results)
                self.insert(data_source)
            else:
                diff = []
                database_ads_ids = [i.ads_id for i in results]
                for result in scrapy_results:
                    if result['ads_id'] not in database_ads_ids:
                        diff.append(result)
                data_source = self.get_data_source(diff)
                if len(diff) > 0:
                    try:
                        client = boto3.client(
                            'sqs',
                            aws_access_key_id=SQS['key'],
                            aws_secret_access_key=SQS['secret']
                        )
                        queue = client.get_queue_by_name(QueueName=SQS['queue'])
                        user = self.get_user(filter_id)
                        msg = json.dumps({
                            'subject': 'Nauji ' + spider.name + ' skelbimai',
                            'email': user.email,
                            'template': 'results',
                            'data': {'filter': filter_id, 'results': data_source}
                        })
                        queue.send_message(MessageBody=msg)
                    except Exception as e:
                        print(e)

                    self.insert(data_source)

    def get_user(self, filter):
        return Filters.get(Filters.id == filter).user

    def insert(self, data_source):
        try:
            with database.atomic():
                for idx in range(0, len(data_source), 100):
                    idx_ = data_source[idx:idx + 100]
                    Results.insert_many(idx_).execute()
        except Exception as e:
            print(e)


