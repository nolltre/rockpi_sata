#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    This module gets the statuses needed for the display, e.g. disk free,
    temperature etc.
"""

import json
import shutil
from datetime import datetime, timedelta

# Requires: netifaces, humanize
import netifaces
import humanize

deg = u'\xb0'


def cpu_temp(as_fahrenheit=False) -> str:
    """ Get the cpu temperature, all operations done in millidegrees Celsius"""
    with open('/sys/class/thermal/thermal_zone0/temp') as temp:
        temp_reading = int(temp.read())

    if as_fahrenheit:
        temperature = (temp_reading * 1.8) + 32000
    else:
        temperature = temp_reading
    return f'{round(temperature / 1000.0, 1)}{deg}' \
        f'{"F" if as_fahrenheit else "C"}'


def uptime() -> str:
    """ Get the time the system's been up. It reads from the /proc/uptime file
    and takes the first argument (num seconds) and formats it into a human
    readable format """
    with open('/proc/uptime') as uptime:
        seconds_up = int(float(uptime.read().split(' ')[0]))

    if seconds_up:
        return humanize.precisedelta(datetime.now()
                                     - timedelta(seconds=seconds_up),
                                     minimum_unit='minutes',
                                     format='%d')
    else:
        return "Could not get uptime"


def get_ips(interfaces=[], ipv6=False) -> str:
    """ Get the IP address associated with each listed interface """
    phys_interfaces = netifaces.interfaces()

    ret_str = ""

    # Only loop through interfaces that actually exists
    for intf in [i for i in phys_interfaces if i in interfaces]:
        addresses = netifaces.ifaddresses(intf)
        ret_str += f'{intf}: {addresses[netifaces.AF_INET][0]["addr"]}\n'

    return ret_str.strip()


def disk_free(mountpoints=[]) -> str:
    # Check mountpoints
    ret_str = ""
    for mount in mountpoints:
        s = shutil.disk_usage(mount)
        mntpoint = mount.split('/')[-1]
        if not mntpoint:
            mntpoint = "Root"
        ret_str += f"{mntpoint}: {int(s.used/s.total*100)}% free\n"

    return ret_str.strip()


def fan_speed() -> str:
    """ Get the duty cycle of the cooling fan (in the top board) """
    with open("/sys/class/pwm/pwmchip0/pwm1/duty_cycle") as sys_duty_cycle:
        duty_cycle = int(sys_duty_cycle.read()) / 1e5

    if duty_cycle:
        return f'Cooling fan at {duty_cycle}%'
    else:
        return f'Cannot read duty cycle of fan'


def set_fan_speed(dutycycles) -> bool:
    with open('/sys/class/thermal/thermal_zone0/temp') as temp:
        temp_reading = int(temp.read()) / 1000.0

    dutycycle_val = min(dutycycles.values(), key=lambda x: abs(x-temp_reading))
    for k, v in dutycycles.items():
        if v == dutycycle_val:
            perc = int(k)

    print(f"Duty cycle should be {perc}%")
    with open("/sys/class/pwm/pwmchip0/pwm1/duty_cycle", "w") as sys_duty_cycle:
        sys_duty_cycle.write(str(int(perc * 1e5)))


def get_config() -> dict:
    with open("config.json") as json_data_file:
        return json.load(json_data_file)


if __name__ == '__main__':
    js_config = get_config()
    print(f"CPU temperature: {cpu_temp()}")
    print(f"CPU temperature: {cpu_temp(True)}")
    print(uptime())
    print(get_ips(interfaces=js_config["interfaces"]))
    print(disk_free(js_config["mountpoints"]))
    print(fan_speed())
    set_fan_speed(js_config["fan"])

# vim: set wrap formatoptions+=t tw=80 noai ts=4 sw=4:
