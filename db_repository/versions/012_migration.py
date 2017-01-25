from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
thermostat = Table('thermostat', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('min', INTEGER),
    Column('max', INTEGER),
    Column('hw_id', VARCHAR(length=40)),
    Column('room_id', INTEGER),
    Column('name', VARCHAR(length=40)),
    Column('enabled', BOOLEAN),
    Column('set', INTEGER),
)

thermostat = Table('thermostat', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('name', String(length=40)),
    Column('enabled', Boolean),
    Column('min', Integer),
    Column('max', Integer),
    Column('desired', Integer),
    Column('hw_id', String(length=40)),
    Column('room_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['thermostat'].columns['set'].drop()
    post_meta.tables['thermostat'].columns['desired'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['thermostat'].columns['set'].create()
    post_meta.tables['thermostat'].columns['desired'].drop()
