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

EXTENSIONS = {
    'Scraper.extensions.Mailer': 500,
}

# Database connection details
DB_SETTINGS = {
    'USER': 'root',
    'PASSWD': 'root',
    'HOST': '127.0.0.1',
    'DB_NAME': 'sif'
}

SITES = {
    'skelbiu': 1,
    'autoplius': 2,
    'aruodas': 3,
}

MAIL = {
    'server': '',
    'user': '',
    'pass': '',
    'port': 587,
    'from': ''
}

SQS = {
    'region': 'eu-central-1',
    'key': '',
    'secret': '',
    'url': ''
}

WEBSITE = 'http://skelbimuseklys.lt/'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'Scraper (+http://www.yourdomain.com)'
