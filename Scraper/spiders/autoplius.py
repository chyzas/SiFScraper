# -*- coding: utf-8 -*-
import urlparse
import scrapy
from Scraper.items import ScraperItem
from scrapy import Request
from Scraper.settings import SITES, DB_SETTINGS
import MySQLdb

NAME = "autoplius"

def get_url_and_ids_from_db():
    conn = MySQLdb.connect(DB_SETTINGS['HOST'], DB_SETTINGS['USER'], DB_SETTINGS['PASSWD'], DB_SETTINGS['DB_NAME'],
                           charset="utf8")
    cursor = conn.cursor()
    query = "SELECT f.id, f.user_id, f.url FROM filter f " \
            "INNER JOIN fos_user u ON f.user_id = u.id " \
            "WHERE f.site_id = %s AND u.enabled = 1 AND f.active = 1" % (SITES[NAME])
    cursor.execute(query)
    return cursor.fetchall()

class AutopliusSpider(scrapy.Spider):
    name = NAME

    allowed_domains = ["autoplius.lt"]

    def start_requests(self):
        items = get_url_and_ids_from_db()
        for id, user_id, url in items:
            yield Request(url, meta={'id': id, 'user_id': user_id})

    def parse(self, response):
        try:
            filter_id = response.meta['id']
            user_id = response.meta['user_id']
            items = response.xpath(".//*[@class='item']")
            for sel in items:
                if len(sel.xpath("./div[@class='item-section fr']/div[@class='price-list price-list-promo rel']")) == 0:
                    item = ScraperItem()
                    item['title'] = self.get_title(sel)
                    item['url'] = urlparse.urljoin(response.url, sel.xpath("./div[@class='item-section fr']/h2[@class='title-list']/a/@href").extract()[0])
                    item['price'] = self.get_price(sel)
                    item['filter_id'] = filter_id
                    item['details'] = self.get_details(sel)
                    yield item

            next_page = response.xpath("(//*[@class='next']/@href)[1]")
            if next_page:
                url = urlparse.urljoin(response.url, next_page.extract()[0])
                yield Request(url, self.parse, meta={'id': filter_id, 'user_id': user_id})
        except Exception as e:
            print e

    def get_title(self, selector):
        xpath = selector.xpath("./div[@class='item-section fr']/h2[@class='title-list']/a/text()")
        raw_title = xpath.extract()[0]
        return raw_title.encode('ascii', errors='ignore').strip()

    def get_price(self, selector):
        x = selector.xpath("./div[@class='item-section fr']/div[@class='price-list']/p[@class='fl']/strong/text()")
        return int(x.extract()[0].replace(' ', '').replace(u'\u20ac', ''))

    def get_details(self, selector):
        path = selector.xpath("./div[@class='item-section fr']/div[@class='param-list']/div/span")
        return ' | '.join([i.xpath("./text()").extract()[0] for i in path])