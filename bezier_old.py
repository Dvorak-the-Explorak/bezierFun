from smooth import *

def interpolate(f, g):
	def result(t):
		return (1-t)*f(t) + t*g(t)
	return result

def bezier(controlPoints):
	if len(controlPoints) == 0:
		raise ValueError("At least 1 control point required for a bezier curve")

	if len(controlPoints) == 1:
		return lambda t: controlPoints[0]

	f = bezier(controlPoints[:-1])
	g = bezier(controlPoints[1:])

	return interpolate(f, g)