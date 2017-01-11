import os, logging
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')


_ch = logging.FileHandler("automation.log", 'a')
_frmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
_ch.setFormatter(_frmt)

LOGGERS = {}
LOGGERS['app.core'] = logging.DEBUG
LOGGERS['app.views'] = logging.DEBUG
LOGGERS['app.onewirethermo'] = logging.DEBUG
LOGGERS['app.cache'] = logging.DEBUG
LOGGERS['app.views'] = logging.DEBUG

for logger, level in LOGGERS.items():
	logging.getLogger(logger).addHandler(_ch)
	logging.getLogger(logger).setLevel(level)
