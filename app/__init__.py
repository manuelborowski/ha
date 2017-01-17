from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

from app import Pins
from app import views, models, cache, core, onewirethermo, zwave

views.init()
Pins.Init()
cache.init()
core.init()
zwave.init()

onewirethermo.start()
zwave.start()


	

