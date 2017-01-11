from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

from app import Pins
from app import views, models, cache, core, onewirethermo

views.init()
Pins.Init()
cache.init()
onewirethermo.init()
core.init()


	

