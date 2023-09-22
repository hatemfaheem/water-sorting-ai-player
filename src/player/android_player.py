import os
import time
from typing import List

from src.common.constants import Constants


class AndroidPlayer:
	"""
	Executes the solution by emulating touch events on the connected phone.
	"""

	def play(self, solution_steps: List[tuple[int, int]], touch_locations: List[tuple[int, int]]):
		for step in solution_steps:
			source, destination = step
			print(f"Pouring {source} in {destination}")
			self._emulate_touch(touch_locations[source][0], touch_locations[source][1])
			time.sleep(0.5)
			self._emulate_touch(touch_locations[destination][0], touch_locations[destination][1])
			time.sleep(2)

	@staticmethod
	def _emulate_touch(x, y):
		os.system(f"{Constants.ADB_PATH} shell input tap {x} {y}")
