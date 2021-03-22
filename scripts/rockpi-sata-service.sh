#!/bin/sh

# TODO: These are the commands to run, and on which terminal

openvt 10 -- /opt/rockpi-sata/status.py cpu_temp
openvt 11 -- /opt/rockpi-sata/status.py fan_speed
openvt 12 -- /opt/rockpi-sata/status.py free_mem
openvt 13 -- /opt/rockpi-sata/status.py uptime
openvt 14 -- /opt/rockpi-sata/status.py disk_free
openvt 15 -- /opt/rockpi-sata/status.py get_ips
# openvt 16 -- /opt/rockpi-sata/status.py get_ipv6s

# TODO: Main script responsible for switching virtual terminals
/opt/rockpi-sata/read_button.py
