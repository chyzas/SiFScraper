# -*- coding: utf-8 -*-

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from scrapy import signals
from scrapy.mail import MailSender
from Scraper.sif_models import *
from Scraper.settings import WEBSITE
from Scraper.settings import MAIL
import logging

logging.basicConfig(filename='extensions.log',level=logging.DEBUG,)


def send_mail(message, title, recipient):
    try:
        msg = MIMEMultipart()
        msg['From'] = MAIL['from']
        msg['To'] = recipient
        msg['Subject'] = title

        msg.attach(MIMEText(message, 'html', _charset='utf-8'))
        mailServer = smtplib.SMTP(MAIL['server'], MAIL['port'])
        mailServer.ehlo()
        mailServer.starttls()
        mailServer.ehlo()
        mailServer.login(MAIL['user'], MAIL['pass'])
        mailServer.sendmail(MAIL['from'], recipient, msg.as_string())
        mailServer.close()
    except Exception as e:
        print e


class Mailer(object):
    def __init__(self, mail):
        self.mail = mail
        self.num_items = 0

    @classmethod
    def from_crawler(cls, crawler):
        mail = MailSender.from_settings(crawler.settings)

        instance = cls(mail)

        crawler.signals.connect(instance.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(instance.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(instance.item_scraped, signal=signals.item_scraped)

        return instance

    def spider_opened(self, spider):
        print 'woohoo'

    def item_scraped(self, item, response, spider):
        self.num_items += 1

    def spider_closed(self, spider, reason):
        items = Results.\
            select(FosUser.email).\
            join(Filter).\
            join(FosUser).\
            join(Websites, on=Filter.site_id == Websites.id).\
            where(Results.is_new == 1).\
            where(Websites.name == spider.name).\
            group_by(FosUser.email).\
            tuples()

        for email in items:
            message = self.format_message(email, spider)
            try:
                send_mail(message, 'info', email[0])
            except Exception as e:
                logging.error(e.message)
                print e.message

    def format_message(self, email, spider):
        results = Results.\
            select(Results, Filter.filter_name).\
            join(Filter).\
            join(FosUser). \
            join(Websites, on=Filter.site_id == Websites.id). \
            where(FosUser.email == email).\
            where(Results.is_new == 1). \
            where(Websites.name == spider.name). \
            group_by(Filter.filter_name)
        msg = ''
        try:
            for filter in results:
                msg += '<h3>' + filter.filter.filter_name + '</h3><br>'
                msg += '<a href="' + WEBSITE + 'user/filter/' + str(filter.filter.id) + '/delete'+'">Atsisakyti</a>'
                msg += '<br>'
                msg += '*' * 20 + '<br>'
                for result in filter.filter.results_set:
                    msg += '<a href="' + result.url + '">' + result.url + '</a>' + '<br>'
                    msg += 'Kaina: <strong>' + result.price + '</strong><br>'
                    msg += result.title + '<br>'
                    msg += result.details + '<br>'
                    msg += '-' * 20 + '<br>'
        except Exception as e:
            print e.message
        start = """\
               <html>
                 <head></head>
                 <body>
                 <br>
            """
        end = """
       </body>
     </html>
     """

        return start + msg + end
