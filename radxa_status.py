#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    This module gets the statuses needed for the display, e.g. disk free,
    temperature etc.
"""

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

    return ret_str


if __name__ == '__main__':
    print(f"CPU temperature: {cpu_temp()}")
    print(f"CPU temperature: {cpu_temp(True)}")
    print(uptime())
    print(get_ips(interfaces=["lo", "eth0"]))

# :vim: set wrap:
