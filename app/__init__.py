import config
if not config.MODULE_TEST:
	from flask import Flask
	from flask_sqlalchemy import SQLAlchemy

	app = Flask(__name__)
	app.config.from_object('config')
	db = SQLAlchemy(app)

	from app import models
	
	if not config.DB_TOOLS:
		from app import Pins
		from app import views, models, cache, core, onewirethermo, zwave, history, do, schedule

		cache.init()
		views.init()
		do.init()
		Pins.Init()
		zwave.init()
		history.init()
		schedule.init()

		onewirethermo.start()
		zwave.start()
		history.start()
		do.start()
		sendmail.start()
		schedule.start()
		core.start()


	

