#!/bin/sh

echo Build SSD1306 overlay
dtc -@ -Hepapr -I dts -O dtb -o /boot/overlays/ssd1306-overlay.dtbo overlays/ssd1306-overlay.dts