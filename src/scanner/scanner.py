from dataclasses import dataclass
from functools import cmp_to_key
from typing import List

import numpy as np
import cv2


@dataclass
class LevelRepresentation:
	touch_locations: List[tuple[int, int]]
	color_locations: List[List[tuple[int, int]]]
	raw_colors: List[List[np.ndarray]]
	tubes: List[List[int]]


class Scanner:
	"""
	The Scanner component takes an image of a level as an input and produces a level representation.
	"""

	ROW_DIFFERENCE_THRESHOLD: int = 50
	IMAGE_BW_COLOR_THRESHOLD: int = 188
	CONTOUR_SIZE_THRESHOLD: int = 100
	COLOR_CELL_DISTANCE_STEP: int = 80
	SUSPICIOUS_COLOR_THRESHOLD: int = 45

	def __init__(self, debug_mode: bool) -> None:
		self.debug_mode = debug_mode

	def scan_level(self, image: np.ndarray):
		touch_locations, color_locations = self._calculate_centers(image)
		raw_colors = self._sense_colors(image, color_locations)
		tubes = self._cluster_colors(raw_colors)
		return LevelRepresentation(
			touch_locations=touch_locations,
			color_locations=color_locations,
			raw_colors=raw_colors,
			tubes=tubes,
		)

	def _compare_centers(self, center_1, center_2):
		"""
		Compare 2 centers for sorting purposes
		"""
		x1, y1 = center_1
		x2, y2 = center_2

		# Assuming the centers are not on the same horizontal line
		# This threshold is set to differentiate between upper row and lower row of tubes
		threshold = self.ROW_DIFFERENCE_THRESHOLD
		if x1 == x2 and y1 == y2:
			return 0
		if abs(y1 - y2) > threshold:
			return 1 if y1 > y2 else -1
		else:
			return 1 if x1 > x2 else -1

	def _calculate_centers(self, image: np.ndarray) -> (List, List):
		"""
		The core function of the Scanner, it takes an image and find where the color tubes are located.
		:param image: An image of a level.
		:return: touch_locations contain location of each tube in order and
			color_locations contain locations of each color cell.
		"""
		img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		img[img != self.IMAGE_BW_COLOR_THRESHOLD] = 0
		img[img == self.IMAGE_BW_COLOR_THRESHOLD] = 255

		# Find contours (these are the tubes actually).
		contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

		# Each contour is a bunch of points, finding the center by averaging all points in a contour.
		contour_centers = []
		for contour in contours:
			center = np.mean(contour, axis=0).tolist()[0]
			center = (int(center[0]), int(center[1]))
			if contour.size >= self.CONTOUR_SIZE_THRESHOLD:
				contour_centers.append(center)

		contour_centers = sorted(contour_centers, key=cmp_to_key(self._compare_centers))

		if self.debug_mode:
			print(f"contour_centers: {contour_centers}")

		# calculate touch centers from contour_centers
		# by going up a few pixels
		touch_locations = [(ccenter[0], ccenter[1] - 120) for ccenter in contour_centers]

		# calculate color centers from contour_centers
		# by going 3 steps upwards
		color_locations = [[center] for center in contour_centers]
		for color_center in color_locations:
			initial_center = color_center[0]
			for i in range(3):
				new_color_center = (initial_center[0], initial_center[1] - (i + 1) * self.COLOR_CELL_DISTANCE_STEP)
				color_center.append(new_color_center)

		# Solver expects color in each array from top to bottom
		# while previous loop have built them bottom to top
		# That's mainly because we start from the contour center and go up
		reversed_color_locations = [color_tube[::-1] for color_tube in color_locations]

		return touch_locations, reversed_color_locations

	def _sense_colors(self, image: np.ndarray, color_locations) -> List:
		"""
		Given the color cells locations in the level image, find the corresponding color.
		"""
		if self.debug_mode:
			print(f"Sensing colors for color_locations: {color_locations}")

		colors = []

		for color_center_group in color_locations:
			color_column = [image[color_center[1]][color_center[0]] for color_center in color_center_group]
			colors.append(color_column)
		return colors

	@staticmethod
	def _hash_color(color_ndarray):
		"""
		Simple hashing function for a single ndarray.
		"""
		return str([color_ndarray[0], color_ndarray[1], color_ndarray[2]])

	def _cluster_colors(self, colors):
		"""
		Takes colors as RGB ndarray and converting them to indexes (0, 1, 2, ..., n).
		"""
		if self.debug_mode:
			print(f"Clustering colors: {colors}")

		table = {}
		next_value = 0
		result = []

		filtered_tubes, empty_tubes = self._detect_empty_tubes(colors)

		if self.debug_mode:
			print(f"detected empty tubes: {empty_tubes}")

		if len(empty_tubes) == 0:
			raise "Couldn't detect any empty tubes"

		for color_tube in filtered_tubes:
			color_index_col = []
			for color in color_tube:
				if self._hash_color(color) not in table:
					table[self._hash_color(color)] = next_value
					next_value += 1
				color_index_col.append(table[self._hash_color(color)])
			result.append(color_index_col)

		# Appending empty tubes at the end
		result += empty_tubes
		return result

	def _is_suspicious_color(self, color: np.ndarray):
		"""
		A suspicious color is one with single value for R, G and B. And that value is lower than a predefined threshold.
		Such a color will be considered part of an empty tube.
		"""
		uniq_values = {color[0], color[1], color[2]}
		return len(uniq_values) == 1 and list(uniq_values)[0] <= self.SUSPICIOUS_COLOR_THRESHOLD

	def _detect_empty_tubes(self, tube_colors):
		"""
		If all colors in a tube are suspicious (check definition above), such a tube will be considered empty.
		"""
		empty_tubes = []
		filtered_tubes = []
		for tube in tube_colors:
			if all([self._is_suspicious_color(c) for c in tube]):
				empty_tubes.append([])
			else:
				filtered_tubes.append(tube)
		return filtered_tubes, empty_tubes
