
.PHONY: main
put:
	ampy --port /dev/ttyUSB0 put src/boot.py
	ampy --port /dev/ttyUSB0 put src/config.py
	ampy --port /dev/ttyUSB0 put src/led.py
	ampy --port /dev/ttyUSB0 put src/main.py

.PHONY: repl
repl:
	picocom /dev/ttyUSB0 -b 115200

