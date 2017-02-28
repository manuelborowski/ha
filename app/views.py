import logging, os
from flask import render_template, request, jsonify, url_for, send_from_directory
import config
from app import Pins, do, app, cache

log = logging.getLogger(__name__)

_menuItems = []

class MenuItem:
	def __init__(self, name):
		self.name = name

def init():
	global _menuItems
	log.info("starting")
	_menuItems=cache.getRoomList()
	_menuItems.append(MenuItem('instellen'))
	_menuItems.append(MenuItem('overzicht'))
	_menuItems.append(MenuItem('uitgangen'))

@app.route("/favicon.ico")
def favicon():
	return(url_for('static',filename='favicon.ico'))


#different html pages    
@app.route("/", methods=['GET', 'POST'])
@app.route("/<string:menuItem>", methods=['GET', 'POST'])
def Index(menuItem=None):
	if menuItem == None: menuItem = cache.getRoomList()[0].name
	log.debug('menuItem : %s' % menuItem)
	if menuItem == 'uitgangen' :
		return render_template("digitalout.html", uptime=GetUptime(), 
			menuItems=_menuItems, pins=do.getPinList())
	elif menuItem == 'overzicht' :
		return render_template("tempoverview.html", uptime=GetUptime(), 
			menuItems=_menuItems, thermostats=cache.getThermostatList())
	elif menuItem == 'instellen' :
		return render_template("setschedule2.html", uptime=GetUptime(), 
			menuItems=_menuItems, schedule=cache.getHeatingScheduleForViewing(),
			daysofweek = config.DAY_OF_WEEK_LIST)
	else:
		return render_template("base.html", uptime=GetUptime(), room=menuItem, 
			menuItems=_menuItems, thermostats=cache.getThermostatList(menuItem))


# ajax GET call this function periodically to read button state
# the state is sent back as json data
@app.route("/_button")
def _button():
    if Pins.ReadButton():
        state = "pressed"
    else:
        state = "not pressed"
    return jsonify(buttonState=state)


#read the thermostats
@app.route("/_sensor/<string:thermostat>")    
def _readSensor(thermostat):
	#desired, measured, active, enabled = cache.getThermostatParameters(thermostat)
	#print("d/m/a/e %d/%d/%d/%d" % (desired, measured, active, enabled))
	#return jsonify(active='on' if active else 'off', enabled='on' if enabled else 'off', measured=measured, desired=desired)
	t = cache.getThermostat(thermostat)
	return jsonify(active='on' if t.active else 'off', \
		enabled='on' if t.enabled else 'off', measured=t.measured, desired=t.desired, \
		batLevel=t.batLevel)
	
#set the state of a thermostat (enable or disable)
@app.route("/_setstate/<string:thermostat>")
def _setState(thermostat):
    state = request.args.get('state')
    if state=="on":
        Pins.LEDon()
        cache.setThermostatEnabled(thermostat, True)
    else:
        Pins.LEDoff()
        cache.setThermostatEnabled(thermostat, False)
    return ""

#set the temperature
@app.route("/_settemperature/<string:thermostat>")
def _setTemperature(thermostat):
    desired = request.args.get('val')
    cache.setThermostatValue(thermostat, desired)
    return ""

#set a digital output
@app.route("/_setDigitalOut/<string:pin>")
def _setDigitalOut(pin):
	state = request.args.get('state')
	if state=='on':
		do.setPinHigh(int(pin))
	else:
		do.setPinLow(int(pin))
	return ""

#get a digital output
@app.route("/_getDigitalOut/<string:pin>")
def _getDigitalOut(pin):
	value = do.getPinValue(int(pin))
	return jsonify(enabled='on' if value else 'off')

#set the heating schedule, version 2
#item : <database-id>-select
@app.route("/_setSchedule2/<string:item>")
def _setSchedule2(item):
	val = request.args.get('val')
	items = item.split('-')
	cache.setHeatingSchedule(int(items[0]), val)
	return ""
	
	
def GetUptime():
    # get uptime from the linux terminal command
    from subprocess import check_output
    output = check_output(["uptime"]).decode("utf-8")   
    # return only uptime info
    uptime = output[output.find("up"):output.find("user")-5]
    return uptime
    
# run the webserver on standard port 80, requires sudo
if __name__ == "__main__":
    Pins.Init()
    app.run(host='0.0.0.0', port=8888, debug=True)

