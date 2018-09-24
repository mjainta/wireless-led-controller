import socket
import time
import ure

from config import config
from led import set_color_by_request


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
                color_data = set_color_by_request(data)
                cl.send(buildResponse("COLOR SET TO:\nRED=%s GREEN=%s BLUE=%s" % (color_data['red'], color_data['green'], color_data['blue'])))
            else:
                cl.send(buildResponse("UNREGISTERED ACTION\r\nPATH: %s\r\nPARAMETERS: %s" % (path, get_parameters)))
    else:
        print("INVALID REQUEST HERE")
        cl.send(buildResponse("INVALID REQUEST"))
        time.sleep(0.5)
    print("CLOSING")
    cl.close()
