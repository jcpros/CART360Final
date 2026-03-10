# This program was created in Arduino Lab for MicroPython

#Resource for I2C onboarding: https://youtu.be/zlKJ5hvfs6s?si=FtEgdQtq3AExagX3
#Sample Code for pressure sensor taken from https://github.com/sparkfun/qwiic_micropressure_py

import rp2
import qwiic_micropressure
import sys
import time
from machine import Pin, I2C, ADC

i2c = I2C(0, scl=Pin("GP13"), sda=Pin("GP12"), freq=400000)


#initializing photoresistor pin
photoPin = Pin("GP26")
photoRead = ADC(photoPin)


def readSensors():
	myMicroPressure = qwiic_micropressure.QwiicMicroPressure()

	if myMicroPressure.is_connected() == False:
		print("The device isn't connected to the system. Please check your connection", \
			file=sys.stderr)
		return
      
	myMicroPressure.begin()

	while True:
		print(photoRead.read_u16()/1000,end=" ")
		print(myMicroPressure.read_pressure(myMicroPressure.kPressureKpa),end=" ")
		print("")
		time.sleep(1)

if __name__ == '__main__':
	try:
		readSensors()
	except (KeyboardInterrupt, SystemExit) as exErr:
		print("\nEnding Example 1")
		sys.exit(0)