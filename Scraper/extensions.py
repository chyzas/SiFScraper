# -*- coding: utf-8 -*-

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from scrapy import signals
from scrapy.mail import MailSender
from Scraper.sif_models import *
from Scraper.settings import WEBSITE
import logging
import boto.sqs
from Scraper.settings import SQS
from boto.sqs.message import RawMessage
import json


logging.basicConfig(filename='extensions.log',level=logging.DEBUG,)

def group_items(data):
    results = {}
    for line in data:
        email = line['email']
        name = line['filter_name']
        if not results.has_key(email):
            results[email] = {}
        if not results[email].has_key(name):
            results[email][name] = []
        results[email][name].append(line['id'])
    return results


class Mailer(object):
    def __init__(self, mail):
        self.mail = mail
        self.num_items = 0

    @classmethod
    def from_crawler(cls, crawler):
        mail = MailSender.from_settings(crawler.settings)

        instance = cls(mail)

        crawler.signals.connect(instance.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(instance.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(instance.item_scraped, signal=signals.item_scraped)

        return instance

    def spider_opened(self, spider):
        print 'woohoo'

    def item_scraped(self, item, response, spider):
        self.num_items += 1

    def spider_closed(self, spider, reason):
        items = Results.\
            select(Results.id, FosUser.email, Filter.filter_name).\
            join(Filter).\
            join(FosUser).\
            join(Websites, on=Filter.site_id == Websites.id).\
            where(Results.is_new == 1).\
            where(Websites.name == spider.name).\
            dicts()
        grouped = group_items(items)
        if grouped and self.num_items != len(items):
            conn = boto.sqs.connect_to_region('eu-west-1',
                                              aws_access_key_id=SQS['key'],
                                              aws_secret_access_key=SQS['secret'])
            queue = conn.get_queue('email')
            for email in grouped:

                msg = RawMessage()
                msg.set_body(json.dumps({
                    'subject': 'Nauji ' + spider.name + ' skelbimai',
                    'email': email,
                    'template': 'results',
                    'data': grouped[email]
                }))
                queue.write(msg)

        for i in items:
            Results.update(is_new=0).where(Results.id == i['id']).execute()
