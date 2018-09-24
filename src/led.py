import machine
import ujson


def cie1931_table():
    # see https://jared.geek.nz/2013/feb/linear-led-pwm
    # the CIE 1931 lightness formula describes how humans actually perceive light
    # using it we can define the pwm signal for the color codes more human friendly
    INPUT_SIZE = 255       # Input integer size
    OUTPUT_SIZE = 1023      # Output integer size
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


def setup_pwm(pwm):
    pwm.freq(500)
    pwm.duty(0)


def set_color_by_request(request_data):
    pwm_data = transfer_data_to_pwm(request_data)
    set_color(pwm_data['red'], pwm_data['green'], pwm_data['blue'])
    return pwm_data

def set_color(red=0, green=0, blue=0):
    red_pwm.duty(red)
    green_pwm.duty(green)
    blue_pwm.duty(blue)


def transfer_data_to_pwm(request_data):
    data = ujson.loads(str(request_data, 'utf-8'))

    for color, strength in data.items():
        try:
            data[color] = int(strength)
        except ValueError:
            data[color] = 0

    print("DATA:", data)
    data_rgb = {
        'red': 0,
        'green': 0,
        'blue': 0,
    }

    if 'hex' in data:
        data_rgb = convert_hex(data['hex'])
    else:
        if 'red' in data:
            data_rgb['red'] = data['red']

        if 'green' in data:
            data_rgb['green'] = data['green']

        if 'blue' in data:
            data_rgb['blue'] = data['blue']

    # Restrict color strengths between 0 and 255
    data_rgb = {color: max(0, min(255, strength)) for color, strength in data_rgb.items()}
    print("DATA_RGB:", data_rgb)
    return rgb_to_pwm(data_rgb)


def rgb_to_pwm(data_rgb):
    data_pwm = {color: cie[strength] for color, strength in data_rgb.items()}

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


LEDS = [machine.Pin(i, machine.Pin.OUT) for i in (0, 4, 5)]
red_pin = machine.Pin(0)
red_pwm = machine.PWM(red_pin)
green_pin = machine.Pin(4)
green_pwm = machine.PWM(green_pin)
blue_pin = machine.Pin(5)
blue_pwm = machine.PWM(blue_pin)

setup_pwm(red_pwm)
setup_pwm(green_pwm)
setup_pwm(blue_pwm)

cie = cie1931_table()
