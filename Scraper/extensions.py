from collections import defaultdict
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from scrapy import signals
from scrapy.mail import MailSender
from Scraper.config import GMAIL
from Scraper.sif_models import *

def group_items(data, item):
    d = defaultdict(list)
    for line in data:
        d[line[item]].append(line[:5])
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
        items = Results.select(
        Filter.filter_name,
        Results.price,
        Results.url,
        Results.title,
        Results.details,
        FosUser.email,
    ).join(Filter).join(FosUser, on=(Filter.user_id == FosUser.id)).where(
        Results.is_new == 1
    ).tuples()
        # 5 -> email key. need to improve that
        grouped = group_items(list(items), 5)
        for user in grouped:
            message = self.format_message(grouped[user])
            send_mail(message, 'info', user)

    def format_message(self, data):
        msg = ''
        filter_group = group_items(data, 0)
        for filter in filter_group:
            msg += '<h3>' +filter + '</h3><br>'
            msg += '*' * 20 + '<br>'
            for line in filter_group[filter]:
                msg += line[2] + '<br>'
                msg += 'Kaina: <strong>' + str(line[1]) + '</strong><br>'
                msg += line[3] + '<br>'
                msg += line[4] + '<br>'
                msg += '-' * 20 + '<br>'
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



