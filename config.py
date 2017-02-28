import os, logging
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

TEST_MODE = False

INVALID_TEMP=-100

DAY_OF_WEEK_LIST = ['maandag', 'dinsdag', 'woensdag', 'donderdag', 'vrijdag', 'zaterdag', 'zondag']

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(BASE_DIR, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = False

CACHE_UPDATE_DB_DELAY = 24 * 3600 
#CACHE_UPDATE_DB_DELAY = 10

CORE_WORKER_DELAY = 1

ZWAVE_DEVICE="/dev/ttyS0"
OPENZWAVE_CONFIG_FILE="ozwconfig"
OPENZWAVE_LOG_LEVEL="Debug"
OPENZWAVE_LOG_FILE="OZW_Log.log"
INVALID_BATTERY_LEVEL=-100

HISTORY_DIR = os.path.join(BASE_DIR, "history")
HISTORY_INTERVAL = 10 * 60	#seconds

DO_NBR_OF_BYTES=2
DO_RARENEE	=	'rarenee'
DO_CVPOMP1	=	'cvpomp1'
DO_CVPOMP2	=	'cvpomp2'
DO_CVPOMP3	=	'cvpomp3'
DO_VVBADKAMER	=	'vvbadkamer'
DO_RABADKAMER	=	'rabadkamer'
DO_RAYANNICK	=	'rayannick'

DO_OUTPUTS = {
	DO_RARENEE : 0,
	DO_CVPOMP1 : 1,
	DO_CVPOMP2 : 2,
	DO_CVPOMP3 : 3,
	DO_VVBADKAMER : 4,
	DO_RABADKAMER : 5,
	DO_RAYANNICK : 6
}

SM_WINDOW = 3600 * 24	#24 hours window
#SM_WINDOW = 20
SM_ENABLE_SEND_MAIL = False

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
LOGGERS['app.do'] = logging.DEBUG	
LOGGERS['app.sendmail'] = logging.DEBUG	
LOGGERS['werkzeug'] = logging.ERROR	
LOGGERS['openzwave'] = logging.ERROR

for logger, level in LOGGERS.items():
	logging.getLogger(logger).addHandler(_ch)
	logging.getLogger(logger).setLevel(level)
