.PHONY: clean install uninstall dkms_module_install dkms_module_uninstall

objects = ssd1306-overlay.dtbo pwm-fan.dtbo
binaries = read_button.py rockpi-sata-service.sh rockpi-sata.sh status.py
service_files = rockpi-sata.service
config = config.json
pwmfan_module = pwm-fan
pwmfan_version = 0.0.1
overlays_dir = $(DESTDIR)$(PREFIX)/boot/overlays/
install_dir = $(DESTDIR)$(PREFIX)/opt/rockpi-sata
service_dir = $(DESTDIR)$(PREFIX)/etc/systemd/system

%.dtbo:
	dtc -@ -Hepapr -I dts -O dtb -o $@ overlays/$*.dts

all: $(objects)

install: all install_overlays
	install -d $(install_dir)
	install -d $(service_dir)
	install -m 755 $(addprefix scripts/, $(binaries)) $(install_dir)
	install -m 644 $(addprefix config/, $(config)) $(install_dir)
	install -m 644 $(addprefix service/, $(service_files)) $(service_dir)

uninstall: uninstall_overlays
	rm $(addprefix  $(install_dir), $(binaries))
	rm $(addprefix  $(install_dir), $(config))
	rm $(addprefix  $(service_dir), $(service_files))
	rmdir $(install_dir)
	-rmdir $(service_dir)

install_overlays:
	install -d  $(overlays_dir)
	install -m 644 $(objects) $(overlays_dir)

uninstall_overlays:
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
