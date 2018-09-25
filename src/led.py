import machine
import ujson
import utime


red_value = 0
green_value = 0
blue_value = 0


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
    pwm_data = extract_color_pwm_data(request_data)
    set_color(pwm_data['red'], pwm_data['green'], pwm_data['blue'])
    return pwm_data

def set_fade_by_request(request_data):
    rgb_data = extract_color_rgb_data(request_data)
    pwm_data = rgb_to_pwm(rgb_data)
    fade_time = extract_fade_time(request_data)
    set_fade(rgb_data, fade_time)
    return pwm_data


def set_color(red=0, green=0, blue=0):
    red_pwm.duty(red)
    green_pwm.duty(green)
    blue_pwm.duty(blue)


def set_fade(target_color, fade_time):
    global red_value, green_value, blue_value
    diff_color = {
        'red': target_color['red'] - red_value,
        'green': target_color['green'] - green_value,
        'blue': target_color['blue'] - blue_value,
    }
    initial_color = {
        'red': red_value,
        'green': green_value,
        'blue': blue_value,
    }
    interval = 20
    current_duration = 0

    while current_duration < fade_time:
        current_duration = current_duration + interval
        current_color = {
            'red': initial_color['red'] + int(current_duration * diff_color['red'] / fade_time),
            'green': initial_color['green'] + int(current_duration * diff_color['green'] / fade_time),
            'blue': initial_color['blue'] + int(current_duration * diff_color['blue'] / fade_time),
        }
        print('COLOR FADE TO:', current_color)
        current_color_pwm = rgb_to_pwm(current_color)
        set_color(current_color_pwm['red'], current_color_pwm['green'], current_color_pwm['blue'])
        red_value = current_color['red']
        green_value = current_color['green']
        blue_value = current_color['blue']
        utime.sleep_ms(interval)

    target_color_pwm = rgb_to_pwm(target_color)
    set_color(target_color_pwm['red'], target_color_pwm['green'], target_color_pwm['blue'])
    red_value = target_color['red']
    green_value = target_color['green']
    blue_value = target_color['blue']
    print('RED_VALUE:', red_value)
    print('GREEN_VALUE:', green_value)
    print('BLUE_VALUE:', blue_value)


def extract_color_rgb_data(request_data):
    data = ujson.loads(str(request_data, 'utf-8'))

    for color, strength in data.items():
        try:
            if color is not 'hex':
                data[color] = int(strength)
            else:
                data[color] = str(strength)
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
    return data_rgb


def extract_color_pwm_data(request_data):
    global red_value, green_value, blue_value
    rgb_data = extract_color_rgb_data(request_data)
    red_value = rgb_data['red']
    green_value = rgb_data['green']
    blue_value = rgb_data['blue']
    return rgb_to_pwm(rgb_data)


def extract_fade_time(request_data):
    data = ujson.loads(str(request_data, 'utf-8'))

    try:
        fade_time = int(data['fade_time'])
    except ValueError:
        fade_time = 0

    return fade_time


def rgb_to_pwm(data_rgb):
    data_pwm = {color: cie[max(0, min(255, strength))] for color, strength in data_rgb.items()}

    return data_pwm

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
