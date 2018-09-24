# This is your main script.
import machine
import socket
import ure
import ujson
import time
import network
import uos


def parse_config_line(line):
    pattern = "(.*)=(.*)"
    line_stripped = line.rstrip('\n')
    return ure.search(pattern, line_stripped).group(1), ure.search(pattern, line_stripped).group(2)

config = {}

if '.env' in uos.listdir():
    config = {parse_config_line(line)[0]:parse_config_line(line)[1] for line in open('.env')}

def do_connect():
    if 'ssid' in config and 'pass' in config:
        sta_if = network.WLAN(network.STA_IF)
        if not sta_if.isconnected():
            print('connecting to network...')
            sta_if.active(True)
            sta_if.connect(config['ssid'], config['pass'])
            while not sta_if.isconnected():
                pass
        print('network config:', sta_if.ifconfig())
    else:
        print('No network config provided, cannot login to Wifi!')

do_connect()

LEDS = [machine.Pin(i, machine.Pin.OUT) for i in (0, 4, 5)]
red_pin = machine.Pin(0)
red_pwm = machine.PWM(red_pin)
green_pin = machine.Pin(4)
green_pwm = machine.PWM(green_pin)
blue_pin = machine.Pin(5)
blue_pwm = machine.PWM(blue_pin)


def cie1931_table():
    # see https://jared.geek.nz/2013/feb/linear-led-pwm
    # the CIE 1931 lightness formula describes how humans actually perceive light
    # using it we can define the pwm signal for the color codes more human friendly
    INPUT_SIZE = 255       # Input integer size
    OUTPUT_SIZE = 1024      # Output integer size
    INT_TYPE = 'const unsigned char'
    TABLE_NAME = 'cie'

    def cie1931(L):
        L = L*100.0
        if L <= 8:
            return (L/902.3)
        else:
            return ((L+16.0)/116.0)**3

    x = range(0,int(INPUT_SIZE+1))
    y = [round(cie1931(float(L)/INPUT_SIZE)*OUTPUT_SIZE) for L in x]
    print(y)
    return y

cie = cie1931_table()

def setup_pwm(pwm):
    pwm.freq(500)
    pwm.duty(0)


def color(red=0, green=0, blue=0):
    red_pwm.duty(red)
    green_pwm.duty(green)
    blue_pwm.duty(blue)

def buildResponse(response):
  # BUILD DE HTTP RESPONSE HEADERS
  return '''HTTP/1.0 200 OK\r\nContent-type: text/html\r\nContent-length: %d\r\n\r\n%s''' % (len(response), response)

def parseURL(url):
  #PARSE THE URL AND RETURN THE PATH AND GET PARAMETERS
  parameters = {}
  
  path = ure.search("(.*?)(\?|$)", url) 
  
  while True:
    vars = ure.search("(([a-z0-9]+)=([a-z0-8.]*))&?", url)
    if vars:
      parameters[vars.group(2)] = vars.group(3)
      url = url.replace(vars.group(0), '')
    else:
      break

  return path.group(1), parameters


def transfer_data_to_pwm(request_data):
    data = ujson.loads(str(request_data, 'utf-8'))
    print("DATA:", data)
    data_rgb = {}

    if 'hex' in data:
        data_rgb = convert_hex(data['hex'])
    else:
        if 'red' in data:
            data_rgb['red'] = data['red']

        if 'green' in data:
            data_rgb['green'] = data['green']

        if 'blue' in data:
            data_rgb['blue'] = data['blue']

    print("DATA_RGB:", data_rgb)
    return rgb_to_pwm(data_rgb)


def rgb_to_pwm(data_rgb):
    data_pwm = {k: cie[v] for k, v in data_rgb.items()}

    return data_pwm

def rgb_value_to_pwm(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return int(rightMin + (valueScaled * rightSpan))

def convert_hex(hex):
    hex = hex.lstrip('#')
    return {k: int(hex[i:i+2], 16) for k, i in {'red': 0, 'green': 2 ,'blue': 4}.items()}


setup_pwm(red_pwm)
setup_pwm(green_pwm)
setup_pwm(blue_pwm)

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(1)

while True:
    cl, addr = s.accept()
    print('client connected from', addr)
    request = cl.recv(1024)
    print(request)
    request = str(request, 'utf-8')

    obj = ure.search("POST (.*?) HTTP\/1\.1", request)
    print(obj)
    if obj:
        print(obj.group(1))
        path, get_parameters = parseURL(obj.group(1))
        if path.startswith("/api/color"):
            match = ure.search('Content-Length: ([0-9]+)\r\n\r\n$', request)
            data = {}

            if match:
                data = cl.recv(int(match.group(1)))
                print("DATA:", data)
                color_data = transfer_data_to_pwm(data)
                color(color_data['red'], color_data['green'], color_data['blue'])
                cl.send(buildResponse("COLOR SET TO:\nRED=%s GREEN=%s BLUE=%s" % (color_data['red'], color_data['green'], color_data['blue'])))
            else:
                cl.send(buildResponse("UNREGISTERED ACTION\r\nPATH: %s\r\nPARAMETERS: %s" % (path, get_parameters)))
    else:
        print("INVALID REQUEST HERE")
        cl.send(buildResponse("INVALID REQUEST"))
        time.sleep(0.5)
    print("CLOSING")
    cl.close()
