# -*- coding: utf-8 -*-
import urlparse
import scrapy
from Scraper.items import ScraperItem
from scrapy import Request
from Scraper.sif_models import *

SKELBIU = "skelbiu"

class SkelbiuSpider(scrapy.Spider):
    name = SKELBIU
    allowed_domains = ["skelbiu.lt"]

    def start_requests(self):
        filters = Filter.select(Filter, FosUser).join(FosUser).where(
            Filter.site == SITES[SKELBIU],
            FosUser.enabled == 1,
            Filter.active == 1
        )
        for filter in filters:
            yield Request(filter.url, dont_filter=True, meta={'id': filter.id, 'user_id': filter.user_id})

    def parse(self, response):
        filter_id = response.meta['id']
        user_id = response.meta['user_id']
        for sel in response.xpath('.//li[@class="simpleAds"]'):
            price = self.get_price(sel)
            item = ScraperItem()
            item['title'] = self.get_title(sel)
            item['url'] = urlparse.urljoin(response.url, sel.xpath('a/@href').extract()[0])
            item['price'] = price if price else ''
            item['filter_id'] = filter_id
            item['details'] = self.get_details(sel)
            item['item_id'] = self.get_id(sel)
            yield item

        next_page = response.xpath(".//*[@id='pagination']/a[contains(@rel,'next')]/@href")
        if next_page:
            url = urlparse.urljoin(response.url, next_page.extract()[0])
            yield Request(url, self.parse, meta={'id': filter_id, 'user_id': user_id})

    def get_title(self, selector):
        raw_title = selector.xpath('.//div[@class="itemReview"]/h3/a/text()').extract()[0]
        return raw_title.encode('ascii', errors='ignore').strip()

    def get_price(self, selector):
        raw_price = selector.xpath('.//div[@class="adsPrice"]/text()').extract()[0]
        if (self.hasNumbers(raw_price)):
            return raw_price.encode('ascii', errors='ignore').strip().replace(' ', '')

        return False

    def get_details(self, selector):
        try:
            return ' '.join(selector.xpath(".//div[@class='itemReview']/div[@class='adsTexts']//text()").extract()).encode('ascii', errors='ignore')
        except Exception as e:
            return ''

    def get_id(self, sel):
        return sel.xpath("@id")[0].root

    def hasNumbers(self, inputString):
        return any(char.isdigit() for char in inputString)


