# -*- coding: utf-8 -*-
from urllib.parse import urlparse
import scrapy
from Scraper.items import ScraperItem
from scrapy import Request
from Scraper.sif_models import *

SKELBIU = "skelbiu"

class SkelbiuSpider(scrapy.Spider):
    name = SKELBIU
    allowed_domains = ["skelbiu.lt"]

    def start_requests(self):
        filters = Filters.select(Filters, Users).join(Users).where(Filters.website == SITES[SKELBIU], Users.enabled == 1, Filters.active == 1)
        for filter in filters:
            yield Request(filter.url, dont_filter=True, meta={'id': filter.id, 'user_id': filter.user_id})

    def parse(self, response):
        filter_id = response.meta['id']
        user_id = response.meta['user_id']
        try:
            for sel in response.xpath('.//li[@class="simpleAds"]'):
                price = self.get_price(sel)
                item = ScraperItem()
                item['title'] = self.get_title(sel)
                item['url'] = urlparse.urljoin(response.url, sel.xpath('a/@href').extract()[0])
                item['price'] = price if price else ''
                item['filter_id'] = filter_id
                item['details'] = self.get_details(sel)
                item['ads_id'] = self.get_ads_id(sel)
                item['image'] = self.get_image(sel)
                yield item
        except Exception as e:
            print(e.message)

        next_page = response.xpath(".//*[@id='pagination']/a[contains(@rel,'next')]/@href")
        if next_page:
            url = urlparse.urljoin(response.url, next_page.extract_first())
            yield Request(url, self.parse, meta={'id': filter_id, 'user_id': user_id})

    def get_title(self, selector):
        return selector.xpath('.//div[@class="itemReview"]/h3/a/text()').extract_first()

    def get_price(self, selector):
        return selector.xpath('.//div[@class="adsPrice"]/text()').extract_first()


    def get_details(self, selector):
        return ' '.join(selector.xpath(".//div[@class='itemReview']/div[@class='adsTexts']//text()").extract())

    def get_ads_id(self, sel):
        return sel.xpath("@id").extract_first()

    def get_image(self, sel):
        return sel.xpath("img/@src").extract_first()
