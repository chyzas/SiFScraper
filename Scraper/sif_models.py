from peewee import *
from settings import *

database = MySQLDatabase(DB_SETTINGS['DB_NAME'], **{'password': DB_SETTINGS['PASSWD'], 'user': DB_SETTINGS['USER']})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class FosUser(BaseModel):
    confirmation_token = CharField(null=True)
    credentials_expire_at = DateTimeField(null=True)
    credentials_expired = IntegerField()
    email = CharField()
    email_canonical = CharField(unique=True)
    enabled = IntegerField()
    expired = IntegerField()
    expires_at = DateTimeField(null=True)
    facebook_access_token = CharField(null=True)
    facebook = CharField(db_column='facebook_id', null=True)
    last_login = DateTimeField(null=True)
    locked = IntegerField()
    password = CharField()
    password_requested_at = DateTimeField(null=True)
    roles = TextField()
    salt = CharField()
    username = CharField()
    username_canonical = CharField(unique=True)

    class Meta:
        db_table = 'fos_user'

class Websites(BaseModel):
    name = CharField(null=True)
    site_url = CharField(null=True)

    class Meta:
        db_table = 'websites'

class Filter(BaseModel):
    active = IntegerField()
    created_at = DateTimeField()
    filter_name = CharField()
    site = ForeignKeyField(db_column='site_id', null=True, rel_model=Websites, to_field='id')
    url = CharField()
    user = ForeignKeyField(db_column='user_id', null=True, rel_model=FosUser, to_field='id')

    class Meta:
        db_table = 'filter'

class MigrationVersions(BaseModel):
    version = CharField(primary_key=True)

    class Meta:
        db_table = 'migration_versions'

class Results(BaseModel):
    added_on = DateTimeField(null=True)
    details = TextField()
    filter = ForeignKeyField(db_column='filter_id', null=True, rel_model=Filter, to_field='id')
    is_new = IntegerField(null=True)
    item = TextField(db_column='item_id')
    price = IntegerField(null=True)
    title = TextField(null=True)
    url = CharField(unique=True)

    class Meta:
        db_table = 'results'

