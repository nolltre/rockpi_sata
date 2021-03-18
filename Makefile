.PHONY: clean install

objects = ssd1306-overlay.dtbo pwm-fan.dtbo

%.dtbo:
	dtc -@ -Hepapr -I dts -O dtb -o $@ overlays/$*.dts

all: $(objects)

install: all
	install -d $(DESTDIR)$(PREFIX)/boot/overlays
	install -m 644 $(objects) $(DESTDIR)$(PREFIX)/boot/overlays

clean:
	rm $(objects)
