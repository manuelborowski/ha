from app import app, cache
import logging, os
from flask import render_template, request, jsonify, url_for, send_from_directory
from app import Pins

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

@app.route("/favicon.ico")
def favicon():
	#print('get icon from : ' + os.path.join(app.root_path, 'static'))
	return(url_for('static',filename='favicon.ico'))
	#return send_from_directory(os.path.join(app.root_path, 'static'),
    #                           'favicon.ico', mimetype='image/vnd.microsoft.icon')
    
@app.route("/", methods=['GET', 'POST'])
@app.route("/<string:menuItem>", methods=['GET', 'POST'])
def Index(menuItem=None):
	if menuItem == None: menuItem = cache.getRoomList()[0].name
	log.debug('menuItem : %s' % menuItem)
	if menuItem == 'overzicht' :
		return render_template("tempoverview.html", uptime=GetUptime(), 
			menuItems=_menuItems, thermostats=cache.getThermostatList())
	elif menuItem == 'instellen' :
		return render_template("setschedule.html", uptime=GetUptime(), 
			menuItems=_menuItems, schedule=cache.getHeatingScheduleList())
	else:
		return render_template("base.html", uptime=GetUptime(), room=menuItem, 
			menuItems=_menuItems, thermostats=cache.getThermostatList(menuItem))

# ajax GET call this function to set led state
# depeding on the GET parameter sent

# ajax GET call this function periodically to read button state
# the state is sent back as json data
@app.route("/_button")
def _button():
    if Pins.ReadButton():
        state = "pressed"
    else:
        state = "not pressed"
    return jsonify(buttonState=state)

@app.route("/_sensor/<string:thermostat>")    
def _readSensor(thermostat):
	#desired, measured, active, enabled = cache.getThermostatParameters(thermostat)
	#print("d/m/a/e %d/%d/%d/%d" % (desired, measured, active, enabled))
	#return jsonify(active='on' if active else 'off', enabled='on' if enabled else 'off', measured=measured, desired=desired)
	t = cache.getThermostat(thermostat)
	return jsonify(active='on' if t.active else 'off', \
		enabled='on' if t.enabled else 'off', measured=t.measured, desired=t.desired, \
		batLevel=t.batLevel)
	

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

@app.route("/_settemperature/<string:thermostat>")
def _setTemperature(thermostat):
    desired = request.args.get('val')
    cache.setThermostatValue(thermostat, desired)
    return ""
	
@app.route("/_setSchedule/<string:item>")
def _setSchedule(item):
	val = request.args.get('val')
	print(item, val)
	items = item.split('-')
	cache.setHeatingSchedule(items[0], items[1], items[2], val)
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

