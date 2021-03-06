# -*- coding: utf-8 -*-

# Scrapy settings for Scraper project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'Scraper'

SPIDER_MODULES = ['Scraper.spiders']
NEWSPIDER_MODULE = 'Scraper.spiders'

USER_AGENT = "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36"

ITEM_PIPELINES = {
    'Scraper.pipelines.MySQLStorePipeline': 1,
}


# Database connection details
DB_SETTINGS = {
    'USER': 'root',
    'PASSWD': 'root',
    'HOST': '127.0.0.1',
    'DB_NAME': 'seklys'
}

SITES = {
    'skelbiu': 1,
    'autoplius': 2,
    'aruodas': 3,
}


SQS = {
    'region': 'eu-central-1',
    'key': '',
    'secret': '',
    'url': '',
    'queue': 'dev_dot_app_dot_default'
}

