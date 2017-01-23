import os, logging
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

INVALID_TEMP=-100

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(BASE_DIR, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = False

ZWAVE_DEVICE="/dev/ttyS0"
OPENZWAVE_CONFIG_FILE="ozwconfig"
OPENZWAVE_LOG_LEVEL="Debug"
OPENZWAVE_LOG_FILE="OZW_Log.log"

HISTORY_DIR = os.path.join(BASE_DIR, "history")
HISTORY_INTERVAL = 10 * 60	#seconds


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
LOGGERS['app.history'] = logging.DEBUG	
LOGGERS['werkzeug'] = logging.ERROR	

for logger, level in LOGGERS.items():
	logging.getLogger(logger).addHandler(_ch)
	logging.getLogger(logger).setLevel(level)
