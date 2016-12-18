#/usr/bin/python3

from gpiozero import Motor, OutputDevice
from time import sleep
from datetime import datetime as dt
from date_utils import right_now, subtract_days, date_str

IS_RUNNING = False
LAST_RUN = subtract_days(right_now(), 1)

class MotorUtil:
	def __init__(self):
		self.enable = OutputDevice(18)
		self.motor = Motor(4, 17)

	def turn_motor(self, duration=5, speed=0.5):
		"""Turns a Pi motor for the specified duration."""
		global IS_RUNNING
		global LAST_RUN

		if IS_RUNNING:
			print("Already running!")
			return

		current_date = right_now()
		if date_str(current_date) == date_str(LAST_RUN):
			print("Already ran in this minute, ignoring.")
			return

		LAST_RUN = right_now()
		IS_RUNNING = True
		print(date_str(LAST_RUN))

		self.enable.on()
		self.motor.forward(speed)
		sleep(duration)
		self.enable.off()

		IS_RUNNING = False
		print("Motor going to idle.")
