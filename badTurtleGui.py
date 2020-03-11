

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
