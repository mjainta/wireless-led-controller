# This is your main script.
import machine
import socket
import ure
import ujson
import time


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

def getPinStatus():
  return LEDS

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

def color(red=0, green=0, blue=0):
    red_pwm.duty(red)
    green_pwm.duty(green)
    blue_pwm.duty(blue)

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
        if path.startswith("/getPinStatus"):
            cl.send(buildResponse("LED STATUS:\n%s" % "\n".join([str(x.value()) for x in getPinStatus()])))
        elif path.startswith("/api/color"):
            match = ure.search('Content-Length: ([0-9]+)\r\n\r\n$', request)
            data = {}

            if match:
                data, addr = cl.recvfrom(int(match.group(1)))
                data = ujson.loads(str(data, 'utf-8'))
                print("DATA:", data)

                color_data = {
                    'red': data.get('red', 0),
                    'green': data.get('green', 0),
                    'blue': data.get('blue', 0),
                }
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
