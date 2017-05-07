from collections import defaultdict
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from scrapy import signals
from scrapy.mail import MailSender
from Scraper.config import GMAIL
from Scraper.sif_models import *
from Scraper.settings import WEBSITE
import logging

logging.basicConfig(filename='extensions.log',level=logging.DEBUG,)

def group_items(data, item):
    d = defaultdict(list)
    for line in data:
        d[line[item]].append(line[:6])
    return d


def send_mail(message, title, recipient):
    print "Sending mail..........."
    gmailUser = GMAIL['USER']
    gmailPassword = GMAIL['PASS']

    msg = MIMEMultipart()
    msg['From'] = gmailUser
    msg['To'] = recipient
    msg['Subject'] = title

    msg.attach(MIMEText(message, 'html'))
    mailServer = smtplib.SMTP('smtp.gmail.com', 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(gmailUser, gmailPassword)
    mailServer.sendmail(gmailUser, recipient, msg.as_string())
    mailServer.close()


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
        items = Results.select(FosUser.email).join(Filter).join(FosUser).join(Websites,
                                                                              on=Filter.site_id == Websites.id).where(
            Results.is_new == 1).where(Websites.name == spider.name).group_by(FosUser.email).tuples()

        for email in items:
            message = self.format_message(email)
            try:
                send_mail(message, 'info', email[0])
            except Exception as e:
                logging.error(e.message)
                print e.message

    def format_message(self, email):
        results = Results.select(Results, Filter.filter_name).join(Filter).join(FosUser).where(FosUser.email == email).where(Results.is_new == 1).group_by(Filter.filter_name)
        msg = ''
        try:
            for filter in results:
                msg += '<h3>' + filter.filter.filter_name + '</h3><br>'
                msg += '<a href="' + WEBSITE + 'user/filter/' + str(filter.filter.id) + '/delete'+'">Atsisakyti</a>'
                msg += '<br>'
                msg += '*' * 20 + '<br>'
                for result in filter.filter.results_set:
                    msg += result.url + '<br>'
                    msg += 'Kaina: <strong>' + str(result.price) + '</strong><br>'
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
