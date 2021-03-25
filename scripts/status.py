#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    This module gets the statuses needed for the display, e.g. disk free,
    temperature etc.
"""

import argparse
import json
import glob
import shutil
import sys

# Requires: netifaces
import netifaces

deg = u'\xb0'
cls = u'\x1b[2J\x1b[H'


def cpu_temp() -> str:
    """ Get the cpu temperature, all operations done in millidegrees Celsius"""
    with open('/sys/class/thermal/thermal_zone0/temp') as temp:
        temp_reading = int(temp.read())

    as_fahrenheit = js_config["f-temp"]
    if as_fahrenheit:
        temperature = (temp_reading * 1.8) + 32000
    else:
        temperature = temp_reading

    temp_str = f'{round(temperature / 1000.0, 1)}{deg}'
    return f'CPU: {temp_str:>{WIDTH-7}}' \
        f'{"F" if as_fahrenheit else "C"}'


def uptime() -> str:
    """ Get the time the system's been up. It reads from the /proc/uptime file
    and takes the first argument (num seconds) and formats it into a readable
    format similar to the uptime command"""
    with open('/proc/uptime') as uptime:
        seconds_up = int(float(uptime.read().split(' ')[0]))

    if seconds_up:
        days = seconds_up//86400
        hours = (seconds_up - days * 86400)//3600
        minutes = (seconds_up - days * 86400 - hours * 3600)//60
        ret_str = 'Up:\n'
        ret_str += (f'''{f"{days} day{'s' if days>1 else ''}": ^{WIDTH}}\n'''
                    f'{f"{hours:02d}:{minutes:02d}": ^{WIDTH}}')
        return ret_str

    else:
        return "Could not get uptime"


def get_ips(ipv6=False) -> str:
    """ Get the IP address associated with each listed interface """
    phys_interfaces = netifaces.interfaces()

    ret_str = ""

    interfaces = js_config["interfaces"]
    # Only loop through interfaces that actually exists
    if ipv6:
        address_type = netifaces.AF_INET6
    else:
        address_type = netifaces.AF_INET
    for intf in [i for i in phys_interfaces if i in interfaces]:
        addresses = netifaces.ifaddresses(intf)
        ret_str += f'{intf}:\n{addresses[address_type][0]["addr"]}\n'

    return ret_str.strip()


def get_ipv6s() -> str:
    return get_ips(ipv6=True)


def disk_free() -> str:
    # Check mountpoints
    mountpoints = js_config["mountpoints"]
    ret_str = ""
    for mount in mountpoints:
        s = shutil.disk_usage(mount)
        mntpoint = mount.split('/')[-1]
        # Empty means root
        if not mntpoint:
            mntpoint = "Root"
        ret_str += (f"{mntpoint}: {s.used/s.total:>{WIDTH-len(mntpoint)-3}.0%}"
                    "\n")

    return ret_str.strip()


def fan_speed() -> str:
    """ Get the duty cycle of the cooling fan (in the top board) """
    try:
        pwm_file = glob.glob("/sys/class/hwmon/hwmon?/pwm1")
        with open(pwm_file[0]) as sys_duty_cycle:
            duty_cycle = int(sys_duty_cycle.read()) / 255

            return f'Fan: {duty_cycle:>10.0%}'
    except Exception:
        return f'Cannot read duty cycle of fan'


def free_mem() -> str:
    with open("/proc/meminfo") as mem:
        mem_inf = mem.read().splitlines()
        mem_stats = dict(s.split(':') for s in mem_inf)
    return str(int(mem_stats["MemTotal"].strip().split(' ')[0]) // 1024)


def get_config(filename) -> dict:
    with open(filename) as json_data_file:
        return json.load(json_data_file)


if __name__ == '__main__':
    # Valid function names
    FUNCS = {"cpu_temp": cpu_temp,
             "fan_speed": fan_speed,
             "free_mem": free_mem,
             "uptime": uptime,
             "disk_free": disk_free,
             "get_ips": get_ips,
             "get_ipv6s": get_ipv6s}
    parser = argparse.ArgumentParser(description='Print information on '
                                     'screen, use this with openvt to print '
                                     ' information on different virtual '
                                     'consoles')
    parser.add_argument('command', choices=FUNCS.keys(),
                        help='The command to run ('
                        + ' '.join([k for k in FUNCS.keys()])
                        + ')',
                        nargs='+',
                        metavar='COMMAND')
    parser.add_argument('--config', default='config.json',
                        help='Define a different configuration file, '
                        'default: %(default)s')
    parser.add_argument('--clear', default=False,
                        action='store_true',
                        help='If specified, the screen will be cleared before'
                        'the output is printed')
    parser.add_argument('--width', default=16,
                        help='Override the width of the display, default: '
                        '%(default)d')

    args = parser.parse_args()
    js_config = get_config(args.config)
    if args.clear:
        sys.stdout.write(cls)
    WIDTH = args.width
    cmd_output = ""
    for cmd in args.command:
        cmd_output += FUNCS[cmd]() + '\n'
    cmd_lines = cmd_output.split('\n')

    # The display is 16 characters wide on the 128x32 OLED
    out_str = ""
    for part_str in [cmd_line[i:i+WIDTH] for cmd_line in cmd_lines for i in
                     range(0, len(cmd_line), WIDTH)]:
        out_str += part_str + '\n'

    # Strip the last newline before writing the output
    sys.stdout.write(out_str.strip())

# vim: set wrap formatoptions+=t tw=80 noai ts=4 sw=4:
