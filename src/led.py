import machine
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


def update_color_values(color_data):
    global red_value, green_value, blue_value
    red_value = color_data['red']
    green_value = color_data['green']
    blue_value = color_data['blue']


def get_current_value():
    global red_value, green_value, blue_value
    return {'red': red_value, 'green': green_value, 'blue': blue_value}


def set_color_by_request(data):
    rgb_data = extract_color_rgb_data(data)
    set_color_rgb(rgb_data)
    return rgb_data


def set_fade_by_request(data):
    rgb_data = extract_color_rgb_data(data)

    try:
        fade_time = int(data['fade_time'])
    except ValueError:
        fade_time = 0

    set_fade(rgb_data, fade_time)
    return rgb_data


def set_color_rgb(color_data):
    color_data_pwm = {key: get_cie(value) for key, value in color_data.items()}
    update_color_values(color_data)
    print('NEW COLOR:', color_data)
    red_pwm.duty(color_data_pwm['red'])
    green_pwm.duty(color_data_pwm['green'])
    blue_pwm.duty(color_data_pwm['blue'])


def set_fade(target_color, fade_time):
    color_current = get_current_value()
    diff_color = {
        'red': target_color['red'] - color_current['red'],
        'green': target_color['green'] - color_current['green'],
        'blue': target_color['blue'] - color_current['blue'],
    }
    initial_color = {
        'red': color_current['red'],
        'green': color_current['green'],
        'blue': color_current['blue'],
    }
    interval = 20
    current_duration = 0

    print('FADE TIME:', fade_time)

    while current_duration < fade_time:
        current_duration = current_duration + interval
        current_color = {
            'red': initial_color['red'] + int(current_duration * diff_color['red'] / fade_time),
            'green': initial_color['green'] + int(current_duration * diff_color['green'] / fade_time),
            'blue': initial_color['blue'] + int(current_duration * diff_color['blue'] / fade_time),
        }
        set_color_rgb(current_color)
        update_color_values(current_color)
        utime.sleep_ms(interval)

    set_color_rgb(target_color)
    update_color_values(target_color)


def extract_color_rgb_data(data):
    for color, value in data.items():
        try:
            if color is not 'hex':
                data[color] = int(value)
            else:
                data[color] = str(value)
        except ValueError:
            data[color] = 0

    print("PARSED DATA JSON:", data)
    data_rgb = {
        'red': 0,
        'green': 0,
        'blue': 0,
    }

    if 'hex' in data:
        data_rgb = convert_hex_to_rgb(data['hex'])
    else:
        if 'red' in data:
            data_rgb['red'] = data['red']

        if 'green' in data:
            data_rgb['green'] = data['green']

        if 'blue' in data:
            data_rgb['blue'] = data['blue']

    # Restrict color values between 0 and 255
    data_rgb = {color: max(0, min(255, value)) for color, value in data_rgb.items()}
    print("PARSED DATA RGB:", data_rgb)
    return data_rgb


def get_cie(value):
    return cie[max(0, min(255, value))]


def convert_hex_to_rgb(hex):
    hex = hex.lstrip('#')
    return {k: int(hex[i:i+2], 16) for k, i in {'red': 0, 'green': 2 ,'blue': 4}.items()}


def setup_pwm(pwm):
    pwm.freq(500)
    pwm.duty(0)


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
