from peewee import *
from settings import *
import datetime

database = MySQLDatabase(DB_SETTINGS['DB_NAME'], **{'password': DB_SETTINGS['PASSWD'],
                                                    'user': DB_SETTINGS['USER'],
                                                    'host': DB_SETTINGS['HOST']})

class BaseModel(Model):
    class Meta:
        database = database

class FailedJob(BaseModel):
    exception = TextField()
    failed_at = DateTimeField()
    payload = TextField()

    class Meta:
        db_table = 'failed_jobs'

class Website(BaseModel):
    name = CharField()
    url = CharField()

    class Meta:
        db_table = 'websites'

class User(BaseModel):
    available_filter_count = IntegerField()
    created_at = DateTimeField()
    email = CharField()
    enabled = IntegerField()
    token = CharField()

    class Meta:
        db_table = 'users'

class Filter(BaseModel):
    activation_token = CharField()
    active = IntegerField()
    created_at = DateTimeField()
    deactivation_token = CharField()
    name = CharField()
    url = TextField()
    user = ForeignKeyField(db_column='user_id', null=True, rel_model=User, to_field='id')
    website = ForeignKeyField(db_column='website_id', null=True, rel_model=Website, to_field='id')

    class Meta:
        db_table = 'filters'

class Result(BaseModel):
    created_at = DateTimeField(default=datetime.datetime.now)
    filter = ForeignKeyField(db_column='filter_id', null=True, rel_model=Filter, to_field='id')
    image = TextField(null=True)
    ads_id = CharField()
    price = CharField(null=True)
    title = TextField(null=True)
    url = CharField()
    details = TextField(null=True)

    class Meta:
        db_table = 'results'

