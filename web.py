import time
from flask import Flask, request, abort
import RPi.GPIO as GPIO
import yaml
import os

config_file = 'config/' + os.environ['FLASK_ENV'] + '.yml'
config = {}
sensors = {}
single_door_sensors_active = True
double_door_sensors_active = True
relays = {}
relay_one_active = True
relay_two_active = True


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if single_door_sensors_active:
        if GPIO.input(16) == GPIO.HIGH and GPIO.input(18) == GPIO.HIGH:
            print("Garage is Opening/Closing")
            return app.send_static_file('Question.html')
        else:
            if GPIO.input(16) == GPIO.LOW:
                print("Garage is Closed")
                return app.send_static_file('Closed.html')
            if GPIO.input(18) == GPIO.LOW:
                print("Garage is Open")
                return app.send_static_file('Open.html')
    else:
        return app.send_static_file('Question.html')


@app.route('/Garage', methods=['GET', 'POST'])
def Garage():
    name = request.form['garagecode']
    if code_is_authorized(name):
        GPIO.output(7, GPIO.LOW)
        time.sleep(1)
        GPIO.output(7, GPIO.HIGH)
        time.sleep(2)

        if single_door_sensors_active:
            if GPIO.input(16) == GPIO.HIGH and GPIO.input(18) == GPIO.HIGH:
                print("Garage is Opening/Closing")
                return app.send_static_file('Question.html')
            else:
                if GPIO.input(16) == GPIO.LOW:
                    print("Garage is Closed")
                    return app.send_static_file('Closed.html')
                if GPIO.input(18) == GPIO.LOW:
                    print("Garage is Open")
                    return app.send_static_file('Open.html')
        else:
            return app.send_static_file('Question.html')
    else:
        if name == "":
            name = "NULL"
        print("Garage Code Entered: " + name)
        if single_door_sensors_active:
            if GPIO.input(16) == GPIO.HIGH and GPIO.input(18) == GPIO.HIGH:
                print("Garage is Opening/Closing")
                return app.send_static_file('Question.html')
            else:
                if GPIO.input(16) == GPIO.LOW:
                    print("Garage is Closed")
                    return app.send_static_file('Closed.html')
                if GPIO.input(18) == GPIO.LOW:
                    print("Garage is Open")
                    return app.send_static_file('Open.html')
        else:
            return app.send_static_file('Question.html')


@app.route('/single', methods=['GET', 'POST'])
def single_door():
    if code_is_authorized(request.args['code']):
        if request.method == 'POST':
            trigger_door_by_pin(relays['two']['pin'])
            return "Ok"
        else:
            if single_door_sensors_active:
                if GPIO.input(sensors['single']['pins'][0]) == GPIO.LOW:
                    print("Garage is Closed")
                    return "Door is closed"
                elif GPIO.input(sensors['single']['pins'][1]) == GPIO.LOW:
                    print("Garage is Open")
                    return "Door is open"

            print("Unable to check single door status")
            return "Door status unknown"
    else:
        print("Bad code: %s" % (request.args['code']))
        abort(401)


@app.route('/double', methods=['GET', 'POST'])
def double_door():
    if code_is_authorized(request.args['code']):
        if request.method == 'POST':
            trigger_door_by_pin(relays['one']['pin'])
        else:
            if double_door_sensors_active:
                if GPIO.input(sensors['double']['pins'][0]) == GPIO.LOW:
                    print("Garage is Closed")
                    return "Door is closed"
                elif GPIO.input(sensors['double']['pins'][1]) == GPIO.LOW:
                    print("Garage is Open")
                    return "Door is open"

            print("Unable to check double door status")
            return "Door status unknown"
    else:
        print("Bad code: %s" % (request.args['code']))
        abort(401)


@app.route('/stylesheet.css')
def stylesheet():
    return app.send_static_file('stylesheet.css')


@app.route('/Log')
def logfile():
    return app.send_static_file('log.txt')


@app.route('/images/<picture>')
def images(picture):
    return app.send_static_file('images/' + picture)


def init_pins():
    """
    The pin numbers refer to the board connector not the chip
    """
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    # Activate the sensors
    for sensor in sensors.keys():
        if sensor['activate']:
            for pin in sensor['pins']:
                GPIO.setup(pin, GPIO.IN, GPIO.PUD_UP)

    # Activate the relays
    for relay in relays.keys():
        if relay['activate']:
            GPIO.setup(relay['pin'], GPIO.OUT)
            GPIO.output(relay['pin'], GPIO.HIGH)


def load_config():
    global config
    global sensors
    global single_door_sensors_active
    global double_door_sensors_active
    global relay_one_active
    global relay_two_active
    global relays

    with open(config_file) as f:
        config = yaml.full_load(f)

    sensors = config['sensors']
    single_door_sensors_active = sensors['single']['activate']
    double_door_sensors_active = sensors['double']['activate']

    relays = config['relays']
    relay_one_active = relays['one']['activate']
    relay_two_active = relays['two']['activate']


def code_is_authorized(code):
    print("code: %s" % (code))
    f = [c for c in config['codes'].keys() if c == code and
         config['codes'][c]['active']]
    if len(f) > 0:
        print('Code assigned to %s' % (config['codes'][code]['user']))
        return True
    else:
        return False


def trigger_door_by_pin(pin):
    GPIO.output(pin, GPIO.LOW)
    time.sleep(1)
    GPIO.output(pin, GPIO.HIGH)
    time.sleep(2)
    return "Ok"


if __name__ == '__main__':
    load_config()
    init_pins()
    app.run(debug=True, host='0.0.0.0', port=5000)
