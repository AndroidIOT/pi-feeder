#/usr/bin/python3

from gpiozero import Motor, OutputDevice
from time import sleep
from datetime import datetime as dt
from date_utils import right_now, subtract_days, date_str

class MotorUtil:
	def __init__(self):
    		
		self.enable = OutputDevice(18)
		self.motor = Motor(4, 17)

		self.is_running = False
		self.last_run = right_now()
		self.last_run = subtract_days(self.last_run, 1)

	def turn_motor(self, duration=5, speed=0.5):
		"""Turns a Pi motor for the specified duration."""
		if self.is_running:
			print("Already running!")
			return

		current_date = right_now()
		if date_str(current_date) == date_str(self.last_run):
			print("Already ran in this minute, ignoring.")
			return

		self.last_run = right_now()
		self.is_running = True

		self.enable.on()
		self.motor.forward(speed)
		sleep(duration)
		self.enable.off()

		self.is_running = False
		print("Motor going to idle.")
