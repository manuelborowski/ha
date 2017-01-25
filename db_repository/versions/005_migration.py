from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
room = Table('room', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('name', String(length=40)),
)

thermostat = Table('thermostat', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('min', Integer),
    Column('max', Integer),
    Column('current', Integer),
    Column('hw_id', String(length=40)),
    Column('room_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['room'].create()
    post_meta.tables['thermostat'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['room'].drop()
    post_meta.tables['thermostat'].drop()
