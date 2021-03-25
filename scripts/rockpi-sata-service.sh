#!/bin/bash

# TODO: These are the commands to run, and on which terminal
REFRESH=5
CONFIG=${CONFIG:-"config.json"}

openvt -f -c 10 -- watch -n $REFRESH -t ./status.py --config "${CONFIG}" cpu_temp fan_speed free_mem
openvt -f -c 11 -- watch -n $REFRESH -t ./status.py --config "${CONFIG}" uptime
openvt -f -c 12 -- watch -n $REFRESH -t ./status.py --config "${CONFIG}" disk_free
openvt -f -c 13 -- watch -n $REFRESH -t ./status.py --config "${CONFIG}" get_ips
# openvt 16 -- /opt/rockpi-sata/status.py get_ipv6s

# TODO: Main script responsible for switching virtual terminals
#/opt/rockpi-sata/read_button.py

# TODO: Kill the watch processes (i.e. save the pids and kill them in a trap)
START_VT=10
NUM_VTS=4
while true; do
    i=$START_VT
    until [ $i -eq $(($START_VT+$NUM_VTS)) ]; do
        chvt $i
        sleep $REFRESH
        ((i=$i+1))
    done
done
