# -*- coding: utf-8 -*-
import urlparse
import scrapy
from Scraper.items import ScraperItem
from scrapy import Request
from Scraper.sif_models import *

NAME = "autoplius"

class AutopliusSpider(scrapy.Spider):
    name = NAME

    allowed_domains = ["autoplius.lt"]

    def start_requests(self):
        filters = Filter.select(Filter, User).join(User).where(
            Filter.website == SITES[NAME],
            User.enabled == 1,
            Filter.active == 1
        )
        for filter in filters:
            yield Request(filter.url, meta={'id': filter.id, 'user_id': filter.user_id})

    def parse(self, response):
        try:
            filter_id = response.meta['id']
            user_id = response.meta['user_id']
            items = response.xpath(".//*[@class='item']")
            for sel in items:
                if len(sel.xpath("./div[@class='item-section fr']/div[@class='price-list price-list-promo rel']")) == 0:
                    item = ScraperItem()
                    url = urlparse.urljoin(response.url, sel.xpath("./div[@class='item-section fr']/h2[@class='title-list']/a/@href").extract()[0])
                    item['title'] = self.get_title(sel)
                    item['url'] = url
                    item['price'] = self.get_price(sel)
                    item['filter_id'] = filter_id
                    item['details'] = self.get_details(sel)
                    item['item_id'] = url.split('-')[-1].split('.')[0]
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