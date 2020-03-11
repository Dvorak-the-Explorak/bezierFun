from smooth import *
# f and g should be FSmooth objects
def interpolate(f, g):
	down = FSmooth([lambda t: 1-t, lambda t: -1])
	up = FSmooth([lambda t: t, lambda t: 1])

	return down*f + up*g


def bezier(controlPoints):
	if len(controlPoints) == 0:
		raise ValueError("At least 1 control point required for a bezier curve")

	if len(controlPoints) == 1:
		return FSmooth.const(controlPoints[0])

	f = bezier(controlPoints[:-1])
	g = bezier(controlPoints[1:])

	return interpolate(f, g)

def drawBezier(turtle, points, curvatureThreshold=0.1, drawControls=True, numTicks=10):
	def drawNormal(path, t, scaling=0.05):
		#save turtle's pen settings
		pen = turtle.pen()

		#get current point
		p = Point(turtle.xcor(), turtle.ycor())

		#calculate speed and velocity
		vel = path[1](t)
		speed = abs(vel)

		#if speed is 0 don't bother drawing the normal
		if speed != 0:
			normal = vel.rotate(pi/2) * (1/speed)
			normal = normal * path.accel(t) * scaling

			turtle.pendown()
			turtle.goto((p + normal).coords)

			#return to inital point
			turtle.penup()
			turtle.goto(p.coords)

		#go back to previous pen settings
		turtle.pen(pen)

	def drawAccel(path, t, scaling=0.05):
		p = Point(turtle.xcor(), turtle.ycor())
		# draw the acceleration vector
		a = path[2](t)
		turtle.goto((p + a*0.05).coords)
		turtle.penup()
		turtle.goto(p.coords)
		turtle.pendown()


	path = bezier(points)

	turtle.tracer(0)
	turtle.penup()
	if drawControls:
		for p in points:
			turtle.goto(p.coords)
			turtle.dot(5)

	t = 0
	if numTicks <2:
		numTicks = 0
	else:
		tickSpacing = 1/(numTicks-1)
		drawNormal(path, t)
	nextTick = tickSpacing
	max_dt = 0.01
	stepSize = 10
	while(t<1):
		p = path(t) + offset
		turtle.goto(p.coords)
		turtle.pendown()
		if t>=nextTick:
			#drawAccel(path, t)
			drawNormal(path, t)
			nextTick += tickSpacing
		dt = max_dt/100
		try:
			dt = stepSize/path.speed(t)
		except ZeroDivisionError:
			pass
		dt = min(max_dt, dt)
		t += dt
	t = 1
	p = path(t) + offset
	turtle.goto(p.coords)
	turtle.pendown()
	drawNormal(path, t)

	turtle.tracer(1)
	turtle.done()

def interactiveBezier(points, curvatureThreshold=0.1):
	def redraw():
		points = [Point(n.xcor(), n.ycor()) for n in nodes]
		path = bezier(points)


		turtle.tracer(0)
		#undraw the line
		while line.undobufferentries():
			line.undo()
		t = 0

		max_dt = 0.03
		min_dt = max_dt/100
		stepSize = 10
		line.penup()
		while(t<1):
			p = path(t)
			line.goto(p.coords)
			line.pendown()

			dt = max_dt
			# dt = max_dt/100
			# try:
			# 	dt = stepSize/path.speed(t)
			# except ZeroDivisionError:
			# 	pass
			dt = min(max_dt, dt)
			t += dt
		t = 1
		p = path(t)
		line.goto(p.coords)

		turtle.update()

	def dragger(node):
		def drag(x,y):
			#ondrag is only called when the mouse actually moves
			node.ondrag(None)
			node.goto(x, y)
			redraw()
			node.ondrag(dragger(node))
			turtle.update()
		return drag


	path = bezier(points)

	#default turtle draws the curve
	line = turtle.Turtle()
	line.penup()
	line.hideturtle()

	nodes = [turtle.Turtle() for p in points]

	turtle.tracer(0)
	for n,p in zip(nodes, points):
		n.penup()
		n.shape('circle')
		n.goto(p.coords)
		n.turtlesize(0.5)
		n.ondrag(dragger(n))
	# turtle.update()

	redraw()

	# turtle.done()
	turtle.Screen().mainloop()


import turtle
from math import pi

points = makePoints([(-150,200), (-50,100), (50,0), (150,200)])

# drawBezier(turtle, points)
interactiveBezier(points)