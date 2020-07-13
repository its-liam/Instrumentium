import numpy as np

def longCall(input_x_list, price, strike):
	"""
	payoff = -(price), x <= strike &= (x - strike) - price, x > strike
	"""
	y = []
	
	for x in input_x_list:
		# piecewise function
		if x <= strike:
			payoff = -(price)
			y.append(payoff)
		elif x > strike:
			payoff = x - strike - price
			payoff = round(payoff, 2)
			y.append(payoff)

	return y


def shortCall(input_x_list, price, strike):
	""" 
	payoff = price, x <= strike &= price - (x - strike), x > strike
	"""
	y = []

	for x in input_x_list:
		if x <= strike:
			payoff = price
			y.append(payoff)
		elif x > strike:
			payoff = price - x + strike
			payoff = round(payoff, 2)
			y.append(payoff)

	return y


def longPut(input_x_list, price, strike):
	""" 
	payoff = strike - x - price, x < strike &= -(price), x > strike
	"""
	y = []

	for x in input_x_list:
		if x < strike:
			payoff = strike - x - price
			payoff = round(payoff, 2)
			y.append(payoff)
		elif x >= strike:
			payoff = -(price)
			y.append(payoff)

	return y


def shortPut(input_x_list, price, strike):
	""" 
	payoff = price - (strike - x), x < strike &= price, x > strike
	"""
	y = []

	for x in input_x_list:
		if x < strike:
			payoff = price + x - strike
			payoff = round(payoff, 2)
			y.append(payoff)
		elif x >= strike:
			payoff = price
			y.append(payoff)

	return y


def longStock(input_x_list, price):
	""" 
	payoff = x - price
	"""
	y = []

	for x in input_x_list:
		payoff = x - price
		payoff = round(payoff, 2)
		y.append(payoff)

	return y


def shortStock(input_x_list, price):
	"""
	payoff = price - x
	"""
	y = []

	for x in input_x_list:
		payoff = price - x
		payoff = round(payoff, 2)
		y.append(payoff)

	return y

def longFutures(input_x_list, delivery_price):
	""" 
	payoff = x - delivery_price
	"""
	y = []

	for x in input_x_list:
		payoff = x - delivery_price
		payoff = round(payoff, 2)
		y.append(payoff)

	return y


def shortFutures(input_x_list, delivery_price):
	"""
	payoff = delivery_price - x
	"""
	y = []

	for x in input_x_list:
		payoff = delivery_price - x
		payoff = round(payoff, 2)
		y.append(payoff)

	return y


def lineType(line_instance):
	""" Determine the line type and return a representative integer """
	instrumentType = line_instance.instrument_type
	if instrumentType == 1:
		# Instrument is an option
		option_type = line_instance.option_type
		option_position = line_instance.position

		if option_type == 1:
			# Option is a call
			if option_position == 1:
				return 1 # 1 = long call
			else:
				return 2 # 2 = short call
		elif option_type == 2:
			# Option is a put
			if option_position == 1:
				return 3 # 3 = long put
			else:
				return 4 # 4 = short put

	elif instrumentType == 2:
		# Instrument is a (long) stock
		return 5 # 5 = long stock

	# Return values meaning:
	# 	1 = long call
	# 	2 = short call
	# 	3 = long put
	# 	4 = short put
	# 	5 = long stock

def _zeroXAxis(begin, end):
	""" Return an array from begin to end for an x axis """
	x = []

	for x_val in range(begin, end):
		x.append(x_val)

	return x

def _zeroYAxis(begin, end):
	""" Return a array of zeros with a lenght of length * 10 + 1 """
	y = []
	length = end - begin

	for z in range(0, length):
		y.append(0)

	return y