class FSmooth:
	def __init__(self, fs):
		self.funcs = fs

	@staticmethod
	def const(val):
		return FSmooth([lambda t: val])

	@staticmethod
	def zero():
		return FSmooth([])

	def __call__(self, *args, **kwargs):
		if len(self.funcs) == 0:
			return 0
		return self.funcs[0](*args, **kwargs)

	def __getitem__(self, index):
		return FSmooth(self.funcs[index:])

	def __add__(self, other):
		funcs = [lambda t,f=f,g=g: f(t) + g(t) for f,g in zip(self.funcs, other.funcs)]
		return FSmooth(funcs)

	def __mul__(self, other):
		from math import factorial as fac
		# nCk
		def binom(n, k):
			# from stackoverflow
			try:
				result = fac(n) // fac(k) // fac(n-k)
			except ValueError:
				result = 0
			return result

		if isinstance(other, FSmooth):
			fs = self.funcs
			gs = other.funcs

			if len(fs) == 0 or len(gs) == 0:
				return FSmooth.zero()

			funcs = []
			for i in range(2*max(len(fs), len(gs))):
				def f(t, i=i):
					result = Point(0,0)
					for j in range(i+1):
						try:
							result += binom(i,j) * fs[j](t) * gs[i-j](t)
						except IndexError:
							pass
					return result
				funcs.append(f)

			return FSmooth(funcs)

		#assume other is a scalar
		funcs = [lambda t,f=f: f(t)*other for f in self.funcs]
		print(funcs)
		return FSmooth(funcs)

	def __rmul__(self, other):
	 	return self*other

	def deriv(self, n):
		return FSmooth(self.funcs[n:])

	def speed(self, t):
		return abs(self.funcs[1](t))
	def accel(self, t):
		return abs(self.funcs[2](t))
	def dist(self, other):
		return abs(self + (-1)*other)


class Point:
	def __init__(self, x, y):
		self.coords = (x,y)
	def rotate(self, angle):
		from math import cos, sin
		x,y = self.coords
		newx = cos(angle)*x - sin(angle)*y
		newy = sin(angle)*x + cos(angle)*y

		return Point(newx, newy)

	def __add__(self, other):
		return Point(self.coords[0] + other.coords[0],
					self.coords[1] + other.coords[1])
	def __mul__(self, s):
		return Point(s*self.coords[0], s*self.coords[1])
	def __rmul__(self,s):
		return self*s
	def __repr__(self):
		return str(self.coords)
	def __abs__(self):
		return sum([x*x for x in self.coords])**0.5
		
def makePoints(ps):
	return [Point(p[0], p[1]) for p in ps]

if __name__ == '__main__':
	f = FSmooth([lambda t: t*t, lambda t: 2*t, lambda t: 2])
	g = 2*f
	print("f = t*t, g = 2*f")
	for i in range(10):
		print(f"f({i}): {f(i)}, f'({i}): {f.deriv(1)(i)}, , f''({i}): {f.deriv(2)(i)}")
		print(f"g({i}): {g(i)}, g'({i}): {g.deriv(1)(i)}, , g''({i}): {g.deriv(2)(i)}")