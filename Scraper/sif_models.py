from peewee import *
from .settings import *

database = MySQLDatabase(DB_SETTINGS['DB_NAME'], **{'password': DB_SETTINGS['PASSWD'],
                                                    'user': DB_SETTINGS['USER'],
                                                    'host': DB_SETTINGS['HOST']})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class FailedJobs(BaseModel):
    exception = TextField()
    failed_at = DateTimeField()
    payload = TextField()

    class Meta:
        table_name = 'failed_jobs'

class Websites(BaseModel):
    name = CharField()
    url = CharField()
    xpath = CharField()

    class Meta:
        table_name = 'websites'

class Users(BaseModel):
    available_filter_count = IntegerField()
    created_at = DateTimeField()
    email = CharField()
    enabled = IntegerField()
    token = CharField()

    class Meta:
        table_name = 'users'

class Filters(BaseModel):
    activation_token = CharField()
    active = IntegerField()
    created_at = DateTimeField()
    deactivation_token = CharField()
    name = CharField()
    url = TextField()
    user = ForeignKeyField(column_name='user_id', field='id', model=Users, null=True)
    website = ForeignKeyField(column_name='website_id', field='id', model=Websites, null=True)

    class Meta:
        table_name = 'filters'

class MigrationVersions(BaseModel):
    version = CharField(primary_key=True)

    class Meta:
        table_name = 'migration_versions'

class Results(BaseModel):
    ads = CharField(column_name='ads_id')
    created_at = DateTimeField()
    details = CharField()
    filter = ForeignKeyField(column_name='filter_id', field='id', model=Filters, null=True)
    image = TextField(null=True)
    price = CharField(null=True)
    title = TextField(null=True)
    url = CharField()

    class Meta:
        table_name = 'results'

