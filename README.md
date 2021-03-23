# rockpi_sata
Scripts for the Rockpi Quad SATA HAT using overlays for Raspberry Pi 4

## Which device?
This is the [RockPi Quad SATA HAT](https://wiki.radxa.com/Dual_Quad_SATA_HAT) that I'm using.

## Why?
Yes, why not just use the provided scripts from [Radxa's Github](https://github.com/akgnah/rockpi-sata)?

My reasons for not being satisfied with the provided scripts are these( in no particular order):  
* Many third party dependencies (pigpiod, python3-rpi.gpio, python3-setuptools, python3-pip, python3-pil, python3-spidev, pigpio, python3-pigpio, etc.) which is fine for some but I don't want them
* Execution of shell scripts through Python
* Modifies my `/boot/config.txt` directly
* Very few comments in the scripts (yeah, yeah, I know good code documents itself and all that jazz, but go ahead and read PEP8 and come back to me)
* Breaks if you disable IPv6 (which I do)
* Poor portability (only supports Raspbian and Ubuntu)
* No console boot messages on the OLED display
* Not using the overlays for the display, gpio key and fan
* Can't boot from a SATA device (the SATA interfaces are enabled through a GPIO output in the script)
* Can't mount encrypted SATA devices with key file without making sure that the scripts are executed in proper order via systemd (which is a major pain point here)


This is a clunky first try to make something that is making heavy use of the built-in capabilities in the boot loader via overlays.


## How does the Rockpi scripts work to initialise the hardware?
I'll try to document my findings here and discuss what I've done to work around them.

### GPIOs involved
There are a few GPIOs that we will need to address to get to grips with some of the shortcomings of the HAT. When started, the GPIOs to wake the SATA interfaces (25 for SATA1/2 and 26 for SATA 3/4) are set to inputs. What that means is basically that the interface isn't going to show up until those GPIOs are set high via the Python scripts.

The SSD1306 OLED display has a reset on GPIO 23 which need to be tripped in order to get the display to initialise itself.

The button can be read on GPIO 17.

The fan in the top board is connected to PWM1 on GPIO 13.

How do we address this? Well, by using the `gpio` option in `/boot/config.txt`, using the `gpio-key` overlay and writing our own overlay for the display and fan of course!

To reiterate, these are the GPIOs I will address first of all:  
| GPIO | Function      |
| ---- | ------------- |
| 13   | Top board fan |
| 17   | Button        |
| 23   | SSD1306 reset |
| 25   | SATA 1/2      |
| 26   | SATA 3/4      |

### Fan
The fan can be enabled by the `pwm` overlay in `/boot/config.txt`:  
```
# Enable PWM channel on GPIO 13 (PWM1)
dtoverlay=pwm,pin=13,func=4
```

I also add a custom overlay (`pwm-fan`) which you can find in the overlays folder.
Do note that you will have to build the kernel module too, which I am doing by copying the `pwm-fan-0.0.1` directory to `/usr/src` and adding it to dkms with `dkms install pwm-fan/0.0.1` which will install the kernel module for you automatically with every kernel update (you'll need the `linux-headers` package too). The pwm-fan.c is copied from `https://github.com/raspberrypi/linux/blob/rpi-5.10.y/drivers/hwmon/pwm-fan.c`  
This should really be made into a script that does this automatically in a package.


### Button
In order to use the button, I'd like it to show up as a normal key which I can read with a program (perhaps Python) via evdev.  
How? Use the `gpio-key` overlay by adding the following into the `/boot/config.txt`:  
```
# Map the GPIO button to KEY_NEXT
dtoverlay=gpio-key,gpio=17,label="Top board",keycode=0x197
```

Which will make it show up in `/dev/input/event0`, for example:  
```
$ evtest /dev/input/event0
Input driver version is 1.0.1
Input device ID: bus 0x19 vendor 0x1 product 0x1 version 0x100
Input device name: "button@11"
Supported events:
  Event type 0 (EV_SYN)
  Event type 1 (EV_KEY)
    Event code 407 (KEY_NEXT)
Properties:
Testing ... (interrupt to exit)
Event: time 1615293751.744343, type 1 (EV_KEY), code 407 (KEY_NEXT), value 1
Event: time 1615293751.744343, -------------- SYN_REPORT ------------
Event: time 1615293751.844339, type 1 (EV_KEY), code 407 (KEY_NEXT), value 0
Event: time 1615293751.844339, -------------- SYN_REPORT ------------
```

### SSD1306 as framebuffer console
There is support to use the SSD1306 fitted to this device as a framebuffer console. To do that, you will have to make your own overlay as the current one doesn't include support for the reset functionality (see the [Kernel documentation](https://www.kernel.org/doc/Documentation/devicetree/bindings/display/ssd1307fb.txt) and [the current Raspberry Pi overlay](https://github.com/raspberrypi/linux/blob/rpi-5.10.y/arch/arm/boot/dts/overlays/ssd1306-overlay.dts)), thus we need to add that:  
```
....
	target = <&i2c1>;
....
        reset-gpios = <&gpio 23 1>;
....
```
The above is in the ssd1306-overlay.dts file in the overlays folder in this repository.

That file is built via the `build_dtbo.sh` script and put in the `/boot/overlays` folder. The following loads it (`/boot/config.txt`):  
```
# Enable the SSD1306 display at boot
dtoverlay=ssd1306-overlay,width=128,height=32,inverted,sequential
```

And adding this to the end of the command line arguments adds the framebuffer capabilites which will give a bunch of boot time messages on the display (`/boot/cmdline.txt`) plus it disables the cursor:  
```
fbcon=font:MINI4x6 fbcon=rotate:2 fbcon=logo-count:0 vt.global_cursor_default=0
```
Do note that I have the enclosure towards me (I can see the disk LEDs), so you might have to modify the rotation of the framebuffer. And I run it headless so there are no other framebuffers competing
Running this in the /etc/rc.local will change the virtual terminal to no. 10 when booted (effectively clearing the screen)
```bash
chvt 10
```

It is very easy to print text if you can just echo to a tty, not so much if you need to print to the framebuffer (unless you want to display images), so the plan is to implement something printing on the different tty's (like disk status on one, CPU stuff on another etc)

### Starting the SATA interfaces at boot
In order to enable both the SATA interfaces at boot time, the following is added to `/boot/config.txt`:  
```
# For the Radxa Quad SATA Hat (26 = SATA1/2 25 = SATA3/4)
gpio=26=op,dh
gpio=25=op,dh
```

That sets the GPIOs as outputs and drives them high.
Don't ask me why the 26 comes before the 25, if I didn't do it this way, the disks would come up in the wrong order (disk 3 as sda, disk 1 as sdc etc.) so it might be wrong in the documentation/wiki.

# Build a Debian package
If you want an installable package `dpkg-buildpackage -b --no-sign` will do that for you

# What doesn't work?
Well, this is just the early stages. There are no scripts to do the functionality
that you can get from the Rockpi repository, but I am willing to accept PR's if
anyone is tempted.  

The Rockpi scripts loads the `w1-gpio` and `w1-therm` kernel modules. In the wiki there's a reference to a couple of GPIOs which I don't know what they are for. One is `GPIO4_C6` which would be GPIO 27 on the Pi and the other one is `ADC_IN0` which is on GPIO 7. The `w1-gpio` listens on GPIO 4 (Raspberry Pi pin 7) per default, but that one isn't used according to the wiki. The Rockpi scripts are trying to read a 1-wire sensor [here](https://github.com/akgnah/rockpi-sata/blob/master/usr/bin/rockpi-sata/fan.py#L33). So perhaps there's a misconfiguration with the Rockpi scripts. I will have to tear the enclosure down and have a look at the pins to understand what's connected where. In the mean time, I'll use the CPU temperature for fan control.

# Plans
Write the scrips needed for displaying information on the screen, controlling what to do when the button is pressed and control the fan speed. The beauty of this is that is should be possible to write the scripts without a lot of dependencies as most functionality is available as files.


I'd like to make it possible to add this as a package for easy maintainability
ideally for Debian/Ubuntu, Arch Linux and Alpine.
