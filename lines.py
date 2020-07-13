# This module is going to simulate a Option class and Asset class which we'll
# ultimately use to create payoff patterns for these types of instruments.
import numpy as np

import inst_functions as inst_fncs

# set constant multipliers
MAX_X_MULTIPLIER = 1.3
MIN_X_MULTIPLIER = 0.6

class Option():
	""" Represents an instance of a Option payoff pattern. """

	def __init__(self, option_type, position, price, strike, calculatable_position, expire_now=True):
		self.instrument_type = 1		# 1 = option; 2 = stock					# we use this property so that when we are looping all line objects we can determine options from stocks
		self.option_type = option_type	# 1 = call; 2 = put
		self.position = position		# 1 = long; 2 = short
		self.price = price
		self.strike = strike
		self.expire_now = expire_now 	# can be expanded on later
		self.max_x = int(strike * MAX_X_MULTIPLIER)
		self.min_x = int(strike * MIN_X_MULTIPLIER)
		self.calculatable_position = calculatable_position
		self.calculated_position = None

		self.x = []						# holds x-coorindate data (function inputs)
		self.y = []						# holds y-coordinate data (function outputs)

		self._updateX()					# used to update self.x				
		self._updateY()					# used to update self.y

	def _updateX(self):
		""" Update self.x dependent on self.max_x """
		self.x = _createXInputs(self.min_x, self.max_x)

	def _updateY(self):
		""" 
		Update self.y dependent on self.inst_type, self.position, self.price, 
		and self.strike, using self.x as input (we call pre-prepared piecewise 
		functions to process the variables for the result).

		Since self._updateY() is called on all option changes, we should 
		calculate breakeven point here, too.
		"""
		if self.option_type == 1:
			# Option is a call
			if self.position == 1:
				# Option is a long call
				self.y = inst_fncs.longCall(self.x, self.price, self.strike)
			elif self.position == 2:
				# Option is a short call
				self.y = inst_fncs.shortCall(self.x, self.price, self.strike)
		elif self.option_type == 2:
			# Option is a put
			if self.position == 1:
				# Option is a long put
				self.y = inst_fncs.longPut(self.x, self.price, self.strike)
			elif self.position == 2:
				# Option is a short put
				self.y = inst_fncs.shortPut(self.x, self.price, self.strike)

		if self.calculatable_position:
			if self.option_type == 1:
				# we're calculating the profit at a specified position for a call option
				if self.position == 1:
					# we're calculating the profit of a long call at a specified position
					self.calculated_position = inst_fncs.longCall(input_x_list=[self.calculatable_position], price=self.price, strike=self.strike)[0]
				else:
					# we're calculating the profit of a short call at a specified position
					self.calculated_position = inst_fncs.shortCall(input_x_list=[self.calculatable_position], price=self.price, strike=self.strike)[0]
			else:
				# we're calculating the profit at a specified position for a put option
				if self.position == 1:
					# we're calculating the profit of a long put at a specified position
					self.calculated_position = inst_fncs.longPut(input_x_list=[self.calculatable_position], price=self.price, strike=self.strike)[0]
				else:
					# we're calculating the profit of a short put at a specified position
					self.calculated_position = inst_fncs.shortPut(input_x_list=[self.calculatable_position], price=self.price, strike=self.strike)[0]


class Asset():
	""" 
	Represents an instance of a financial Asset payoff (i.e. long/short stock 
	position). 
	"""
	def __init__(self, price, position, calculatable_position):
		self.instrument_type = 2		# 1 = option; 2 = stocks				# as mentioned in option class, this is to defferentiate between stocks and options in other functions
		self.position = position		# 1 = long; 2 = short
		self.price = price
		self.max_x = int(price * MAX_X_MULTIPLIER)
		self.min_x = int(price * MIN_X_MULTIPLIER)
		self.calculatable_position = calculatable_position
		self.calculated_position = None

		self.x = []
		self.y = []

		self._updateX()					# initialise self.x
		self._updateY()					# initialise self.y

	def _updateX(self):
		""" Update self.x dependent on self.max_x """
		self.x = _createXInputs(self.min_x, self.max_x)

	def _updateY(self):
		""" 
		Update self.y dependent on self.position and self.price (we call 
		one of two functions that process a linear function) using self.x as 
		input. 
		"""
		if self.position == 1:
			self.y = inst_fncs.longStock(self.x, self.price)
		else:
			self.y = inst_fncs.shortStock(self.x, self.price)

		if self.calculatable_position:
			if self.position == 1:
				# calculate profit for long position in asset at price $self.calculatable_position
				self.calculated_position = round((self.calculatable_position - self.price), 2)
			else:
				# calculate profit for short position in asset at price $self.calculatable_position
				self.calculated_position = round((self.price - self.calculatable_position), 2)


class Futures():
	""" 
	Represents an instance of a financial Asset payoff (i.e. long/short stock 
	position). 
	"""
	def __init__(self, delivery_price, position, calculatable_position):
		self.instrument_type = 2		# 1 = option; 2 = stocks				# as mentioned in option class, this is to defferentiate between stocks and options in other functions
		self.position = position		# 1 = long; 2 = short
		self.delivery_price = delivery_price
		self.max_x = int(price * MAX_X_MULTIPLIER)
		self.min_x = int(price * MIN_X_MULTIPLIER)
		self.calculatable_position = calculatable_position
		self.calculated_position = None

		self.x = []
		self.y = []

		self._updateX()					# initialise self.x
		self._updateY()					# initialise self.y

	def _updateX(self):
		""" Update self.x dependent on self.max_x """
		self.x = _createXInputs(self.min_x, self.max_x)

	def _updateY(self):
		""" 
		Update self.y dependent on self.position and self.price (we call 
		one of two functions that process a linear function) using self.x as 
		input. 
		"""
		if self.position == 1:
			self.y = inst_fncs.longFutures(self.x, self.delivery_price)
		else:
			self.y = inst_fncs.longFutures(self.x, self.delivery_price)


class ProfitLine():
	""" 
	A Profit Line object which averages all given lines to return the overall postion. 
	"""
	def __init__(self, lines_list, min_x, max_x, calculatable_position):
		self.instrument_type = 3
		self.max_x_range = max_x
		self.lines_List = lines_list
		self.calculatable_position = calculatable_position
		self.calculated_position = None

		self.x = _createXInputs(min_x, max_x)
		self.y = []

		self._createProfitLineY()

	def _createProfitLineY(self):
		""" 
		Generate the overall profit position of a set of Lines and update the output 
		variable, self.y. 
		"""
		if not self.calculatable_position:
			# we don't have a specific calculated position to calculate
			count = 0
			y = []

			while count < len(self.x):
				payoff_at_x = 0

				for line in self.lines_List:
					payoff_at_x += line.y[count]

				y.append(payoff_at_x)
				count += 1

			self.y = y
		else:
			# we must calculate profit at a certain position
			count = 0
			y = []
			target = self.calculatable_position

			search_flag = True
			prior_value = None

			while count < len(self.x):
				payoff_at_x = 0

				for line in self.lines_List:
					payoff_at_x += line.y[count]

				# search algorithm for desired profit value
				if search_flag:
					if self.x[count] >= target:
						# we've just calculating the profit pattern point for 
						# the desired profit position or have JUST passed it...
						self.calculated_position = round(payoff_at_x, 2)
						search_flag = False

				y.append(payoff_at_x)
				count += 1

			self.y = y
		


def _createXInputs(begin, end):
	""" 
	Use np.linspace to return a Numpy array of decimals starting at $begin and 
	ending at $end with 1/10 decimal intervals. 
	"""
	# linspace(start number, end number, numpy array length)
	if end <= 100:
		length = end*10 + 1
	elif end > 100 and end <= 500:
		length = end + 1
	elif end > 500 and end <= 1000:
		length = int(end/10) + 1
	else:
		length = int(end/20) + 1

	return np.linspace(begin, end, end*10 + 1)


def updateSmallestX(lines_list, largest_x):
	""" Loop through all lines in $lines_list and return largest $self.max_x """
	lowest_min_x = 0

	for line in lines_list:
		if line.min_x < largest_x:
			lowest_min_x = line.min_x

	return lowest_min_x


def updateLargestX(lines_list):
	""" Loop through all lines in $lines_list and return largest $self.max_x """
	largest_max_x = 0

	for line in lines_list:
		if line.max_x > largest_max_x:
			largest_max_x = line.max_x

	return largest_max_x


def updateInstruments(lines_list, min_x_range, max_x_range):
	""" 
	Given $max_x_range, loop through all lines in $lines_list, update their 
	self.max_x property and call self._updateX() and self._updateY() on all of 
	them. 

	Why do this? This will lead to a graph that is completely filled out from 
	side-to-side. If we don't, some instruments will end sooner and some later, 
	the graph will look unproffesional, and there will be profit pattern 
	summation errors.
	"""
	for line in lines_list:
		line.max_x = max_x_range
		line.min_x = min_x_range
		line._updateX()
		line._updateY()

def JSONtoLines(json):
	""" 
	Accept a JSON data, convert it to a Python Dictionary, and turn the data 
	stored in it into a List of Lines 
	"""
	lines = []
	for line in json.values():
		if line["instrument_type"] == 1:
			# create a option
			if line["option_type"] == 1:
				if line["position"] == 1:
					new_line = Option(option_type=1, position=1,
						price=line["price"], strike=line["strike"])
				else:
					new_line = Option(option_type=1, position=2, 
						price=line["price"], strike=line["strike"])
			else:
				if line["position"] == 1:
					new_line = Option(option_type=2, position=1,
						price=line["price"], strike=line["strike"])
				else:
					new_line = Option(option_type=2, position=2,
						price=line["price"], strike=line["strike"])
		elif line["instrument_type"] == 2:
			# create a stock
			if line["position"] == 1:
				new_line = Asset(price=line["price"], position=1)
			else:
				new_line = Asset(price=line["price"], position=2)
		lines.append(new_line)

	return lines



if __name__ == "__main__":
	test_no = 3
	if test_no == 1:
		# Create a short put with price $5 and strike $55
		option_1 = Option(2, 2, 5, 55, None)
		print(option_1.x)
		print(option_1.y)
	elif test_no == 2:
		# Create a stock/asset position with a S_0 of $45
		asset_1 = Asset(45)
		print(asset_1.x)
		print(asset_1.y)
	elif test_no == 3:
		option_2 = Option(1, 1, 10, 40, None)
		print(option_2.x)
		print(option_2.y)