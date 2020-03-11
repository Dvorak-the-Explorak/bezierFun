from abc import abstractmethod

def polyEvalFn(coeffs, t):
	def eval(t):
		result = 0
		for i in range(len(coeffs)-1,-1,-1):
			result = result*t + coeffs[i]
		return result
	return eval

class FPoly:
	def __init__(self, coeffs):
		self.coeffs = coeffs

	@staticmethod
	def const(val):
		return FPoly([val])

	@staticmethod
	def zero():
		return FPoly([0])

	def __call__(self, t):
		if len(self.coeffs) == 0:
			return 0

		# evaluate polyonomial
		result = 0
		for i in range(len(self.coeffs)-1,-1,-1):

			result = result*t + self.coeffs[i]
		return result

	def __getitem__(self, index):
		return self.deriv(index)

	def __add__(self, other):
		if not isinstance(other, FPoly):
			raise NotImplementedError("Combinations of poly and smooth not implemented")
		coeffs = [a + b for a,b in zip(self.coeffs, other.coeffs)]
		return FPoly(coeffs)
	def __radd__(self, other):
		return self + other

	def __mul__(self, other):

		if isinstance(other, FPoly):
			order = len(self.coeffs)+len(other.coeffs)-1
			coeffs = [Point(0,0)] * order



			for n in range(order):
				lo = max(0, n - (len(other.coeffs)-1))
				hi = min(n+1, len(self.coeffs))
				for i in range(lo, hi):
					a = self.coeffs[i]
					b = other.coeffs[n-i]
					coeffs[n] +=  a*b

			return FPoly(coeffs)
		elif isinstance(other, FSmooth):
			return other * self
			# raise NotImplementedError("Combinations of poly and smooth not implemented")

		#assume other is a scalar
		coeffs = [c*other for c in self.coeffs]
		return FPoly(coeffs)

	def __rmul__(self, other):
	 	return self*other

	def deriv(self, n):
		coeffs = self.coeffs
		while n>0:
			coeffs = coeffs[1:] 
			for i in range(len(coeffs)):
				coeffs[i] *= i + 1
			n -= 1
		return FPoly(coeffs)

	def speed(self, t):
		return abs(self.deriv[1](t))
	def accel(self, t):
		return abs(self.deriv[2](t))

class FSmooth:
	def __init__(self, fs):
		self.funcs = fs

	@staticmethod
	def const(val):
		return FSmooth([lambda t: val])

	@staticmethod
	def zero():
		return FSmooth([])

	@staticmethod
	def fromPolyCoeffs( coeffs):
		funcs = []
		order = len(coeffs)
		for _ in range(order):
			def f(t, coeffs=coeffs[:]):
				result = 0
				for i in range(len(coeffs)-1,-1,-1):
					result = result*t + coeffs[i]
				return result
			funcs.append(f)
			coeffs.pop(0)
			for i in range(len(coeffs)):
				coeffs[i] *= i+1

		return FSmooth(funcs)

	@staticmethod
	def fromFPoly(fpoly):
		if not isinstance(fpoly, FPoly):
			raise ValueError("Can only convert from an Fpoly object")
		
		funcs = []
		for i in range(len(fpoly.coeffs)):
			funcs.append(lambda t,i=i: fpoly.deriv(i)(t))
		return FSmooth(funcs)

	def __call__(self, *args, **kwargs):
		if len(self.funcs) == 0:
			return 0
		return self.funcs[0](*args, **kwargs)

	def __getitem__(self, index):
		return self.deriv(index)

	def __add__(self, other):
		if isinstance(other, FSmooth):
			funcs = [lambda t,f=f,g=g: f(t) + g(t) for f,g in zip(self.funcs, other.funcs)]
			return FSmooth(funcs)
		if isinstance(other, FPoly):
			return self + FSmooth.fromFPoly(other)
		#assume other is a scalar
		print("Warning, adding scalar to function is untested")
		funcs = self.funcs[:]
		funcs[0] = lambda t: self.funcs[0] + other
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
		if isinstance(other, FPoly):
			return self * FSmooth.fromFPoly(other)

		#assume other is a scalar
		funcs = [lambda t,f=f: f(t)*other for f in self.funcs]
		return FSmooth(funcs)

	def __rmul__(self, other):
	 	return self*other

	def deriv(self, n):
		return FSmooth(self.funcs[n:])

	def speed(self, t):
		return abs(self.deriv[1](t))
	def accel(self, t):
		return abs(self.deriv[2](t))

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
		if isinstance(other, Point):
			return Point(self.coords[0] + other.coords[0],
						self.coords[1] + other.coords[1])
		return Point(self.coords[0] + other, self.coords[1] + other)
	def __radd__(self, other):
		return self + other
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
	ts = [0,1,2,3]
	print(f"t={ts} for all examples")

	print("=================")
	print("Using FSmooth:")
	print("=================")
	print("\tf=t^2")
	f = FSmooth.fromPolyCoeffs([0,0,1])
	print("f:", [f(t) for t in ts])
	print("f':", [f[1](t) for t in ts])
	print("f'':", [f[2](t) for t in ts])
	print("\tg = 2f")
	g = f*2
	print("g:", [g(t) for t in ts])
	print("g':", [g[1](t) for t in ts])
	print("g'':", [g[2](t) for t in ts])


	print("\n=================")
	print(  "Using FPoly:")
	print(  "=================")
	print("\tf=t^2")
	f = FPoly([0,0,1])
	print("f:", [f(t) for t in ts])
	print("f':", [f[1](t) for t in ts])
	print("f'':", [f[2](t) for t in ts])
	print("\tg = 2f")
	g = f*2
	print("g:", [g(t) for t in ts])
	print("g':", [g[1](t) for t in ts])
	print("g'':", [g[2](t) for t in ts])

	print("\n=========================")
	print(  "Using FSmooth.fromFPoly:")
	print(  "=========================")
	print("\tf=t^2")
	f = FSmooth.fromFPoly(FPoly([0,0,1]))
	print("f:", [f(t) for t in ts])
	print("f':", [f[1](t) for t in ts])
	print("f'':", [f[2](t) for t in ts])
	print("\tg = 2f")
	g = f*2
	print("g:", [g(t) for t in ts])
	print("g':", [g[1](t) for t in ts])
	print("g'':", [g[2](t) for t in ts])