# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import MySQLdb
from time import strftime
from settings import DB_SETTINGS

class ScraperPipeline(object):
    def process_item(self, item, spider):
        return item


class MySQLStorePipeline(object):
    def __init__(self):

        self.conn = MySQLdb.connect(DB_SETTINGS['HOST'], DB_SETTINGS['USER'], DB_SETTINGS['PASSWD'],
                                    DB_SETTINGS['DB_NAME'], charset="utf8")
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        try:
            self.cursor.execute("""INSERT INTO results (filter_id, is_new, price, url, title, added_on, details)
                VALUES (%s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE is_new = 0 """,
                                (
                                    item['filter_id'],
                                    1,
                                    item['price'],
                                    item['url'],
                                    item['title'],
                                    strftime("%Y-%m-%d %H:%M:%S"),
                                    item['details']
                                ))
            self.conn.commit()

        except MySQLdb.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])

        return item
