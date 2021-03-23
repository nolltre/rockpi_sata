obj-m += pwm-fan.o

all: pwm-fan.c
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules

pwm-fan.c:
	curl -OJL https://raw.githubusercontent.com/raspberrypi/linux/rpi-5.10.y/drivers/hwmon/pwm-fan.c

clean:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean

dist-clean: clean
	-rm pwm-fan.c
