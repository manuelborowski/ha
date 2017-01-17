from app import app, cache
import logging, os
from flask import render_template, request, jsonify, url_for, send_from_directory
from app import Pins

log = logging.getLogger(__name__)

def init():
	log.info("starting")


@app.route("/favicon.ico")
def favicon():
	#print('get icon from : ' + os.path.join(app.root_path, 'static'))
	return(url_for('static',filename='favicon.ico'))
	#return send_from_directory(os.path.join(app.root_path, 'static'),
    #                           'favicon.ico', mimetype='image/vnd.microsoft.icon')
    
@app.route("/", methods=['GET', 'POST'])
@app.route("/<string:room>", methods=['GET', 'POST'])
def Index(room=None):
	if room == None: room = cache.getRoomList()[0].name
	log.debug('room : %s' % room)
	if room == 'instellen' :
		return render_template("setschedule.html", uptime=GetUptime(), 
			rooms=cache.getRoomList(), schedule=cache.getHeatingScheduleList())
	else:
		return render_template("base.html", uptime=GetUptime(), room=room, 
			rooms=cache.getRoomList(), thermostats=cache.getThermostatList(room))

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
	desired, measured, active, enabled = cache.getThermostatParameters(thermostat)
	#print("d/m/a/e %d/%d/%d/%d" % (desired, measured, active, enabled))
	return jsonify(active='on' if active else 'off', enabled='on' if enabled else 'off', measured=measured, desired=desired)
	

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

