# -*- coding: utf-8 -*-
import urlparse
import scrapy
from Scraper.items import ScraperItem
from scrapy import Request
from Scraper.settings import SITES, DB_SETTINGS
import MySQLdb

SKELBIU = "skelbiu"


def get_url_and_ids_from_db():
    conn = MySQLdb.connect(DB_SETTINGS['HOST'], DB_SETTINGS['USER'], DB_SETTINGS['PASSWD'], DB_SETTINGS['DB_NAME'],
                           charset="utf8")
    cursor = conn.cursor()
    query = "SELECT id, user_id, url FROM filter WHERE site_id = %s" % (SITES[SKELBIU])
    cursor.execute(query)
    return cursor.fetchall()


class SkelbiuSpider(scrapy.Spider):
    name = SKELBIU
    allowed_domains = ["skelbiu.lt"]

    def start_requests(self):
        items = get_url_and_ids_from_db()
        for id, user_id, url in items:
            yield Request(url, meta={'id': id, 'user_id': user_id})

    def parse(self, response):
        filter_id = response.meta['id']
        user_id = response.meta['user_id']
        for sel in response.xpath('.//li[@class="simpleAds"]'):
            item = ScraperItem()
            item['title'] = self.get_title(sel)
            item['url'] = urlparse.urljoin(response.url, sel.xpath('a/@href').extract()[0])
            item['price'] = self.get_price(sel)
            item['filter_id'] = filter_id
            yield item

        next_page = response.xpath(".//a[@id='nextLink']/@href")
        if next_page:
            url = urlparse.urljoin(response.url, next_page.extract()[0])
            yield Request(url, self.parse, meta={'id': filter_id, 'user_id': user_id})

    def get_title(self, selector):
        raw_title = selector.xpath('.//div[@class="itemReview"]/h3/a/text()').extract()[0]
        return raw_title.encode('ascii', errors='ignore').strip()

    def get_price(self, selector):
        raw_price = selector.xpath('.//div[@class="adsPrice"]/text()').extract()[0]
        return raw_price.encode('ascii', errors='ignore').strip().replace(' ', '')


