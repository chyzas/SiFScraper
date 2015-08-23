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
    'skelbiu': 1
}

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'Scraper (+http://www.yourdomain.com)'
