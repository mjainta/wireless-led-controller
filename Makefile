
.PHONY: main
main:
	ampy --port /dev/ttyUSB0 run -n src/main.py

.PHONY: repl
repl:
	picocom /dev/ttyUSB0 -b 115200

