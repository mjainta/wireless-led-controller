import machine
import socket
import ure
import ujson

LEDS = [machine.Pin(i, machine.Pin.OUT) for i in (0, 4, 5)]
red_pin = machine.Pin(0)
red_pwm = machine.PWM(red_pin)
green_pin = machine.Pin(4)
green_pwm = machine.PWM(green_pin)
blue_pin = machine.Pin(5)
blue_pwm = machine.PWM(blue_pin)


def setup_pwm(pwm):
    pwm.freq(500)
    pwm.duty(0)


def color(red=0, green=0, blue=0):
    red_pwm.duty(red)
    green_pwm.duty(green)
    blue_pwm.duty(blue)

setup_pwm(red_pwm)
setup_pwm(green_pwm)
setup_pwm(blue_pwm)

color(0,0,1000)


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

print(parseURL('/getPinStatus/0'))
print(parseURL('/getPinStatus?red=1000&blue=1100'))

request = b'GET /getPinStatus/ HTTP/1.1\r\nHost: 192.168.4.1\r\nUser-Agent: HTTPie/0.9.8\r\nAccept-Encoding: gzip, deflate\r\nAccept: application/json, */*\r\nConnection: keep-alive\r\nContent-Type: application/json\r\nContent-Length: 13\r\n\r\n'

match = ure.search(b'Content-Length: ([0-9]+)\r\n\r\n$', request)
print(match == True)
print(match)
if match:
    print(int(match.group(1)))

jsonstr = b'{"red": 1000}'
jsonobj = ujson.loads(jsonstr)
print(jsonobj)
print(jsonobj['red'])

