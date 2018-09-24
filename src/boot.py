import network

from config import config


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
