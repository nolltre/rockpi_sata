.PHONY: clean install uninstall dkms_module_install dkms_module_uninstall

objects = ssd1306-overlay.dtbo pwm-fan.dtbo
pwmfan_module = pwm-fan
pwmfan_version = 1.0
overlays_dir = $(DESTDIR)$(PREFIX)/boot/overlays/

%.dtbo:
	dtc -@ -Hepapr -I dts -O dtb -o $@ overlays/$*.dts

all: $(objects)

install: all dkms_module_install
	install -d  $(overlays_dir)
	install -m 644 $(objects) $(overlays_dir)

uninstall: dkms_module_uninstall
	rm $(addprefix  $(overlays_dir), $(objects))

dkms_module_install:
	# Install the files for DKMS
	dkms add -m $(pwmfan_module) -v $(pwmfan_version)
	dkms install -m $(pwmfan_module) -v $(pwmfan_version)

dkms_module_uninstall:
	dkms uninstall -m $(pwmfan_module) -v $(pwmfan_version)
	dkms remove -m $(pwmfan_module) -v $(pwmfan_version)

clean:
	-rm $(objects)
