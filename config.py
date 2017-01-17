import os, logging
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = False

ZWAVE_DEVICE="/dev/ttyS0"
OPENZWAVE_LOG_LEVEL="Debug"
OPENZWAVE_LOG_FILE="OZW_Log.log"


_ch = logging.FileHandler("automation.log", 'a')
_frmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
_ch.setFormatter(_frmt)

LOGGERS = {}
LOGGERS['app.core'] = logging.DEBUG
LOGGERS['app.views'] = logging.DEBUG
LOGGERS['app.onewirethermo'] = logging.DEBUG
LOGGERS['app.cache'] = logging.DEBUG
LOGGERS['app.views'] = logging.DEBUG
LOGGERS['app.zwave'] = logging.DEBUG
LOGGERS['werkzeug'] = logging.ERROR	

for logger, level in LOGGERS.items():
	logging.getLogger(logger).addHandler(_ch)
	logging.getLogger(logger).setLevel(level)
