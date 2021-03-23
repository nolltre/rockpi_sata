obj-m += pwm-fan.o

download_pwm_fan:
	curl -OJL https://raw.githubusercontent.com/raspberrypi/linux/rpi-5.10.y/drivers/hwmon/pwm-fan.c

all: download_pwm_fan
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules

clean:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean
