# -*- coding: utf-8 -*-
import urlparse
import scrapy
from Scraper.items import ScraperItem
from scrapy import Request
from Scraper.sif_models import *

NAME = "aruodas"

class AutopliusSpider(scrapy.Spider):
    name = NAME

    allowed_domains = ["aruodas.lt"]

    def start_requests(self):
        filters = Filter.select(Filter, FosUser).join(FosUser).where(
            Filter.site == SITES[NAME],
            FosUser.enabled == 1,
            Filter.active == 1
        )
        for filter in filters:
            yield Request(filter.url, meta={'id': filter.id, 'user_id': filter.user_id})

    def parse(self, response):
        try:
            filter_id = response.meta['id']
            user_id = response.meta['user_id']
            items = response.xpath(".//*[@class='list-row  ']")
            ths = response.xpath(".//table[@class='list-search']/thead/tr/th/text()").extract()[2:]
            for sel in items:
                item = ScraperItem()
                item['title'] = ', '.join(sel.xpath(".//*[@class='list-adress ']/h3/a/text()").extract())
                item['url'] = sel.xpath(".//*[@class='list-adress ']/h3/a/@href").extract_first()
                item['price'] = sel.xpath(".//*[@class='list-adress ']/div[@class='price']/span[@class='list-item-price']/text()").extract_first()
                item['filter_id'] = filter_id
                item['details'] = self.get_details(sel, ths)
                item['item_id'] = sel.xpath(".//*[@class='list-remember']/div/@data-id").extract_first()
                yield item

            disabled = response.xpath(".//*[@class='pagination']/a[last()][contains(@class, 'page-bt-disabled')]").extract_first()
            if not disabled:
                url = urlparse.urljoin(response.url, response.xpath(".//*[@class='pagination']/a[last()]/@href").extract_first().extract_first())
                yield Request(url, self.parse, meta={'id': filter_id, 'user_id': user_id})
        except Exception as e:
            print e


    def get_details(self, sel, keys):
        values = [i.xpath('text()').extract_first().strip() for i in sel.xpath(".//td")[2:-1]]
        return ' | '.join([value + ": " + unicode(values[key]) for key, value in enumerate(keys)])