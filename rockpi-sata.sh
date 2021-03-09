#!/bin/sh
set -x

if ! id -u; then
  echo Restarting as root
  sudo "$0" "$@"
  exit $?
fi

exists() {
  # Check if a file/directory exists
  stat "$1" >/dev/null 2>&1
}

wait() {
  # Waits until a folder/file exists, $1 = what to watch
  while ! exists "$1"; do sleep .3; done
}

# For the Radxa Quad SATA Hat (25 = SATA1/2 26 = SATA3/4)
# OLED, on/off GPIO 23
echo Export GPIO pins and make sure they are enabled
GPIO=/sys/class/gpio
for I in 25 26
do
  if ! exists ${GPIO}/gpio${I}; then
    echo ${I} > ${GPIO}/export
    wait ${GPIO}/gpio${I}/value
  fi
  if ! grep out ${GPIO}/gpio${I}/direction; then
    echo out > ${GPIO}/gpio${I}/direction
    sleep .2
  fi
  echo 1 > ${GPIO}/gpio${I}/value
done

# For the fan, on PWM1
PWMCHIP=/sys/class/pwm/pwmchip0
PWM=${PWMCHIP}/pwm1
# Enable PWM1 if it's not already enabled
if ! exists ${PWM}; then
  echo 1 > ${PWMCHIP}/export
  sleep .2
  wait ${PWM}/period
fi
echo 10000000 > ${PWM}/period
echo 6000000 > ${PWM}/duty_cycle
echo 1 > ${PWM}/enable

