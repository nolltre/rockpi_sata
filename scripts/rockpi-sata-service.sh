#!/bin/bash
set -u

REFRESH=${REFRESH:-5}
CONFIG=${CONFIG:-"config.json"}
START_VT=10
SCREENS=(
    "cpu_temp fan_speed free_mem"
    "uptime"
    "disk_free"
    "get_ips"
)
NUM_VTS=${#SCREENS[@]}

function cleanup() {
    # Kill anything started on any TTY we're using
    for ((i = $START_VT; i < $START_VT+$NUM_VTS; i++)); do
        echo Killing processes on tty$i
        pkill -t tty$i
        clear > /dev/tty$i
        deallocvt $i
    done
}

trap cleanup EXIT

for ((i = 0; i < $NUM_VTS; i++)); do
    openvt -f -c $((START_VT+i)) -- watch -n $REFRESH -t ./status.py --config "${CONFIG}" ${SCREENS[$i]}
done

# TODO: Main script responsible for switching virtual terminals
#/opt/rockpi-sata/read_button.py

# Loop indefinely and change terminals every $REFRESH seconds
while true; do
    i=$START_VT
    until [ $i -eq $(($START_VT+$NUM_VTS)) ]; do
        echo Changing to VT $i
        chvt $i
        sleep $REFRESH
        ((i=$i+1))
    done
done
