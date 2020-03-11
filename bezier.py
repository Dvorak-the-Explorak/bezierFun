from smooth import *

class ScreenInfo:
	def __init__(self, width, height):
		self.width = width
		self.height = height
		self.buttons = []
		self.guiScale = 100

	def left(self):
		return -self.width//2
	def right(self):
		return self.width//2
	def top(self):
		return self.height//2
	def bottom(self):
		return -self.height//2
	def addButton(self, name):
		self.buttons.append(name)
	def drawButtons(self, turtle):
		if len(self.buttons) == 0:
			return

		turtle.penup()
		x = self.left() + self.guiScale
		turtle.goto(x, self.top()+3)
		turtle.pensize(3)
		turtle.pendown()
		turtle.goto(x, self.bottom()-3)

		turtle.pensize(3)
		for i,name in enumerate(self.buttons):
			ytop = self.top() - (i)*self.guiScale
			ybot = self.top() - (i+1)*self.guiScale

			#todo better estimate of text width
			textwidth = len(name)
			turtle.penup()
			turtle.goto((self.left() + x)/2, (ytop+ybot)/2)
			turtle.pendown()
			turtle.write(name)			
			turtle.penup()


			turtle.goto(self.left(), ybot)
			turtle.pendown()
			turtle.goto(x, ybot)

	def buttonClickCheck(self, x, y):
		if x-self.left() > self.guiScale:
			return None
		if self.top() - y > len(self.buttons)*self.guiScale:
			return None
		return self.buttons[int((self.top() - y)/self.guiScale)]


# f and g should be FSmooth objects
def interpolate(f, g, FType=FSmooth):
	if FType is FSmooth:
		down = FSmooth([lambda t: 1-t, lambda t: -1])
		up = FSmooth([lambda t: t, lambda t: 1])
	elif FType is FPoly:
		down = FPoly([1,-1])
		up = FPoly([0,1])

	return down*f + up*g


def bezier(controlPoints, FType=FSmooth):
	if len(controlPoints) == 0:
		raise ValueError("At least 1 control point required for a bezier curve")

	if len(controlPoints) == 1:
		return FType.const(controlPoints[0])

	f = bezier(controlPoints[:-1], FType)
	g = bezier(controlPoints[1:], FType)

	return interpolate(f, g, FType)

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
	import turtle
	from math import pi

	def redraw():
		points = [Point(n.xcor(), n.ycor()) for n in nodes]
		path = bezier(points, FPoly)


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

	def newDragger(node):
		def newDrag(x,y):
			#ondrag is only called when the mouse actually moves
			node.ondrag(None)
			node.goto(x, y)
			node.ondrag(dragger(node))
			turtle.update()
		return newDrag

	def newReleaser(node):
		#place the new node in its spot
		def newRelease(x, y):
			node.onrelease(None)
			node.ondrag(None)
			node.goto(x, y)
			node.color('black')
			#this node is added to the bezier control points
			nodes.insert(selected+1, node)
			redraw()
			node.ondrag(dragger(node))
			node.onclick(setSelected(selected+1))
			#nodes further on in the list have the wrong value for setselected
			for i in range(selected+2, len(nodes)):
				nodes[i].onclick = setSelected(i)
			turtle.update()
		return newRelease

	def checkGuiClick(x, y):
		nonlocal selected

		btn = screen.buttonClickCheck(x,y)
		if btn is None:
			return

		if btn == 'Duplicate' and selected is not None:
			newNode = turtle.Turtle()
			newNode.penup()
			newNode.shape('circle')
			newNode.color('red')
			newNode.goto(nodes[selected].xcor(), nodes[selected].ycor())
			newNode.turtlesize(0.5)
			newNode.ondrag(newDragger(newNode))
			newNode.onrelease(newReleaser(newNode))
			turtle.update()
		if btn == "Delete" and selected is not None and selected < len(nodes):
			removed = nodes.pop(selected)
			removed.hideturtle()
			#hopefully turtle object is GC'd when hidden and no references to it left
			for i in range(selected, len(nodes)):
				nodes[i].onclick(setSelected(i))
			redraw()
			turtle.update()

		if btn:
			print(btn)

	def setSelected(n):
		def func(x,y):
			nonlocal selected
			if selected is not None:
				nodes[selected].color('black')
			selected = n
			if selected is not None:
				nodes[selected].color('blue')
		return func

	turtle.tracer(0)

	screen = ScreenInfo(1000,800)
	screen.addButton("Copy (after)")
	screen.addButton("Delete")

	# turtle.setup(screen.width, screen.height)

	path = bezier(points)

	#default turtle draws the curve
	line = turtle.Turtle()
	line.penup()
	line.hideturtle()

	#for drawing other stuff
	misc = turtle.Turtle()
	misc.hideturtle()
	screen.drawButtons(misc)

	nodes = [turtle.Turtle() for p in points]
	selected = 0


	for i,(n,p) in enumerate(zip(nodes, points)):
		n.penup()
		n.shape('circle')
		n.goto(p.coords)
		n.turtlesize(0.5)
		n.ondrag(dragger(n))
		n.onclick(setSelected(i))
	nodes[selected].color('blue')

	redraw()
	turtle.onscreenclick(checkGuiClick)
	turtle.done()

if __name__ == '__main__':
	points = makePoints([(-150,200), (-50,100), (50,0), (150,200)])

	# drawBezier(turtle, points)
	interactiveBezier(points)