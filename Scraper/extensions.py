from collections import defaultdict
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from scrapy import signals
from scrapy.mail import MailSender
from Scraper.settings import DB_SETTINGS
from Scraper.config import GMAIL
import MySQLdb


def get_items_from_db():
    conn = MySQLdb.connect(DB_SETTINGS['HOST'], DB_SETTINGS['USER'], DB_SETTINGS['PASSWD'], DB_SETTINGS['DB_NAME'],
                           charset="utf8")
    cursor = conn.cursor()

    query = "SELECT f.filter_name, r.price, r.url, r.title, r.details, u.`email` from results r " \
            "INNER JOIN `filter` f on r.filter_id = f.id " \
            "INNER JOIN fos_user u on f.user_id = u.id WHERE r.`is_new` = 1"
    cursor.execute(query)
    return cursor.fetchall()


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
        items = get_items_from_db()
        grouped = group_items(items, 5)
        if items != self.num_items:
            for user in grouped:
                message = self.format_message(grouped[user])
                send_mail(message, 'info', user)

    def format_message(self, data):
        msg = ''
        filter_group = group_items(data, 0)
        for filter in filter_group:
            msg += filter + '<br'
            msg += '*' * 10 + '<br>'
            for line in filter_group[filter]:
                msg += line[2] + '<br>'
                msg += 'Price ' + str(line[1]) + '<br>'
                msg += line[3] + '<br>'
                msg += line[4] + '<br>'
                msg += '-' * 10 + '<br>'
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



