import uos
import ure


def parse_config_line(line):
    pattern = "(.*)=(.*)"
    line_stripped = line.rstrip('\n')
    return ure.search(pattern, line_stripped).group(1), ure.search(pattern, line_stripped).group(2)


config = {}

if '.env' in uos.listdir():
    config = {parse_config_line(line)[0]:parse_config_line(line)[1] for line in open('.env')}
