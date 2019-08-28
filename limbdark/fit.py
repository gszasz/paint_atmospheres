## This module contains the class Fit as well as the constants that this class uses
# The range of mu, [0, 1], is split into several intervals. 
# The model is linear in the parameters of the fit on each interval.
# The constraints on the function: the intensity at mu = 1 is set, 
#		the function is continuous everywhere in its domain 

import numpy as np
import math
import scipy.special as sp
import matplotlib.pyplot as plt
import util as ut

## functions on a given interval
# the non-zero functions on a given interval
f = [lambda _: 1, lambda x: x, lambda x: x**2, lambda x: x**3, lambda x: x**4]
# the number of non-zero functions on a given interval
n = len(f)
# zero functions on a given interval
fz = [lambda _: 0] * n

## the values of mu in Castelli and Kurucz 2004, reversed
mu_arr = np.array([0.01, 0.025, 0.05, 0.075, 0.1, 0.125, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.])

# number of steps in mu for monotonicity checks
mu_step = 0.001
# array of mu values for which the fitted intensity functions should be discretely monotonic
mu_check_arr = np.arange(0, 1, mu_step)

class Fit:
	""" Class containing intensity vs mu for some temperature and gravity, 
		along with the corresponding fit """

	# the boundaries for the intervals of the fit: [0, x0], [x0, x1], ... [x(n), 1]
	muB_arr = np.array([])
	# the tuples of boundaries
	muB_tup = []
	# the number of intervals
	m = 0	
	# mu array split into a list of arrays according to the boundaries
	mu_arr_split = np.array([])
	# all the functions on each interval
	F = []
	# the model for the given complete set of mu values
	x = []

	# sets the array of boundary values between mu intervals
	# then splits the array of mu values accordingly, then computes all the functions on all the intervals
	# and the linear model for all the given mu values
	@classmethod
	def set_muB(cls, b):
		# set the array of boundaries
		cls.muB_arr = np.array(b)
		# set the number of intervals
		cls.m = len(b) + 1
		# set the array of tuples describing the intervals
		cls.muB_tup = []
		cls.muB_tup.append((0, b[0]))
		for c in range(len(b) - 1):
			cls.muB_tup.append((b[c], b[c+1]))
		cls.muB_tup.append((b[-1], 1))
		# set local variables for this function
		muB_arr = cls.muB_arr
		m = cls.m
		# split the array of Kurucz's mu values according to the boundaries between intervals
		cls.mu_arr_split = np.split(mu_arr, np.searchsorted(mu_arr, muB_arr))
		# include the boundaries twice, both in the interval on the left and the interval on the right
		for i in range(m - 1):
			cls.mu_arr_split[i] = np.append(cls.mu_arr_split[i], cls.mu_arr_split[i + 1][0])
		# compute all the functions on each interval
		for i in range(m):
			cls.F.append(fz * i + f + fz * (m - i - 1))
		## compute the model for the given complete set of mu values
		# stack the column obtained from applying to each value of mu all the functions 
		# on that value's interval
		xl = []
		for i in range(m): # interval
			Fi = cls.F[i] # all functions on this interval
			for mu in cls.mu_arr_split[i]: # mu on this interval
				xj = [func(mu) for func in Fi]
				xl.append(np.array(xj))
		cls.x = np.array(xl)

	# initialize an object of this class with an array of intensities corresponding to the array 
	# of mu values in this module and the wavelength, log g and temperature of this fit;
	# compute the fit
	def __init__(self, I_arr, wl, g, temp, ch):
		self.wl = wl
		self.g = g
		self.temp = temp
		self.I_arr = I_arr
		# for the linear algebra fit,
		# duplicate the intensity values at the boundaries of mu intervals
		I_arr_dup = np.copy(I_arr)
		ind = len(I_arr_dup) - 1
		for i in reversed(range(self.m - 1)):
			sub_ind = len(self.mu_arr_split[i + 1]) - 1
			ind -= sub_ind
			I_arr_dup = np.insert(I_arr_dup, ind, I_arr_dup[ind])
		# fit
		alpha = np.linalg.lstsq(self.x, I_arr_dup, rcond=None)[0]
		self.p = alpha
		if ch:
			self.check()

	# intensity vs mu in terms of computed parameters
	# mu has to be in [0, 1]
	def I(self, mu):
		i = np.searchsorted(self.muB_arr, mu, side='right') # interval where this mu value is found
		Fi = self.F[i] # all the functions on this interval
		I = sum(self.p * [func(mu) for func in Fi])
		return I

	# Given the upper integration boundary phi1, for each function of the fit on each interval of the fit, 
	# computes twice the integral of the function as a function of mu = a * cos(phi) + b,
	# on the intersection of the interval and [0, phi1]
	@classmethod
	def integrate(cls, phi1, a, b):
		# phi in terms of mu
		def mu(phi):
			return a * math.cos(phi) + b
		# mu in terms of phi
		def phi(mu):
			cosn = (mu - b) / a
			if cosn > 1 or cosn < -1:
				return np.NAN
			else:
				return math.acos(cosn)
		# indefinite integrals of the non-zero fit functions as functions of phi,
		# w.r.t. phi on interval i, given the evaluated elliptic integral; 
		# this function should be modified if the fit functions change
		def intgrt(phi):
			# cosine phi
			cosn = math.cos(phi)
			cos2 = math.cos(2*phi)
			sine = math.sin(phi)
			sin2 = math.sin(2*phi)
			sin3 = math.sin(3*phi)
			sin4 = math.sin(4*phi)
			# integral of the polynomial
			integr = [
				phi,
				b*phi + a*sine,
				(a**2/2. + b**2)*phi + (2*a*b + (a**2*cosn)/2.)*sine,
				((3*a**2*b)/2. + b**3)*phi + ((5*a**3)/6. + 3*a*b**2 + \
					(3*a**2*b*cosn)/2. + (a**3*cos2)/6.)*sine,
				((3*a**4)/8. + 3*a**2*b**2 + b**4)*phi + (3*a**3*b + 4*a*b**3)*sine + \
					(a**4/4. + (3*a**2*b**2)/2.)*sin2 + (a**3*b*sin3)/3. + (a**4*sin4)/32.
			]
			return np.array(integr)
		# initialize the total integral for function on each interval
		result = np.zeros(n * cls.m)
		# find the values of mu that correspond to the two integration boundaries:
		# mu(phi1) and mu(0) should be between 0 and 1
		mu0, mu1 = [mu(phi1), mu(0)]
		# go through the mu intervals in the order of increasing mu values
		# this corresponds to going through the phi intervals in the order of decreasing phi values
		for i, interval in enumerate(cls.muB_tup):
			phiL = np.NAN; phiU = np.NAN # initialize the integration boundaries for this interval
			# setting the upper integration limit on phi, which corresponds to
			# setting the lower limit on mu
			if mu0 >= interval[0] and mu0 < interval[1]: 
				phiU = phi1
			if mu0 < interval[0]: 
				phiU = phi(interval[0])
			# setting the lower integration limit on phi, which corresponds to
			# setting the upper limit on mu
			if mu1 >= interval[0] and mu1 < interval[1]:
				phiL = 0
			if mu1 >= interval[1]:
				phiL = phi(interval[1])
			# if both the upper and the lower limits of integration are defined for this interval
			if not np.isnan(phiL) and not np.isnan(phiU):
				# compute the integral on this interval
				result[i * n : (i + 1) * n] += intgrt(phiU) - intgrt(phiL)
		return 2 * result


	# variable containing the minimum I(mu = 0) / I(mu = 1), the wavelength, the gravity and the temperature 
	# where this occurs; can be negative
	I0_min = [np.inf, -1, -1, -1]
	# variable containing the minimum value of intensity difference across a mu step divided by
	# I(mu = 1), the wavelength, the gravity, the temperature and the mu where this occurs; can be negative
	min_step = [np.inf, -1, -1, -1, -1]
	# maximum deviation of the fitted function from the given values of intensity divided by I(mu = 1),
	# the wavelength, the gravity, the temperature and the mu where this occurs; cannot be negative
	max_dev = [0, -1, -1, -1, -1]

	# check that the fit is good
	# adjusts class variable to contain information about the worst fits so far:
	# the value at mu = 0, the maximum difference between adjacent values of mu, 
	# the maximum difference between the fit function and the given intensity values
	def check(self):
		vI = np.vectorize(self.I) # vectorized version of the intensity function
		I1 = self.I_arr[-1] # given intensity value at mu = 1
		I0 = self.I(0) # the fitted function evaluated at zero value
		# value at zero
		if I0 == 0:
			if self.I0_min[0] >= 0:
				type(self).I0_min = [0, self.wl, self.g, self.temp]
		elif I1 != 0:
			I0_rel = I0 / I1
			if I0_rel < self.I0_min[0]:
				type(self).I0_min = [I0_rel, self.wl, self.g, self.temp]
		# monotonicity
		I_check_arr = vI(mu_check_arr)
		diff = np.diff(I_check_arr)
		ind = np.argmin(diff)
		ms = diff[ind]
		if ms == 0:
			if self.min_step[0] >= 0:
				type(self).min_step = [0, self.wl, self.g, self.temp, mu_check_arr[ind]]
		elif I1 != 0:
			ms_rel = ms / I1
			if ms_rel < self.min_step[0]:
				type(self).min_step = [ms_rel, self.wl, self.g, self.temp, mu_check_arr[ind]]
		# goodness of fit
		diff = vI(mu_arr) - self.I_arr
		ind = np.argmax(diff)
		md = np.abs(diff[ind])
		if I1 == 0 and md != 0:
			type(self).max_dev = [np.inf, self.wl, self.g, self.temp, mu_arr[ind]]
		else:
			if md == 0:
				md_rel = 0
			else:
				md_rel = md / I1
			if md_rel > self.max_dev[0]:
				type(self).max_dev = [md_rel, self.wl, self.g, self.temp, mu_arr[ind]]
		return

	# plot the information in this object
	def plot(self):
		I_arr = self.I_arr
		wl = self.wl
		g = self.g
		temp = self.temp
		params = self.p
		print(params)
		# construct the label string
		lab = ""
		c = 0 # count
		i = 0 # interval
		for a in params:
			if c % n == 0:
				i += 1
				if i != 1:
					lab = lab + '\n'
				lab = lab + 'a' + str(i) + ': '
			lab = lab + '%.2E '
			c += 1
		# construct the offsets of data from the edges of the plot
		delta_y = np.max(I_arr) - np.min(I_arr)
		offset_y = delta_y * 0.1
		# vectorized version of the intesity vs mu function
		vI = np.vectorize(self.I)

		fig = plt.figure()
		plt.axes().set_ylim([np.min(I_arr) - offset_y, np.max(I_arr) + offset_y])
		plt.scatter(mu_arr, I_arr, marker='o', c='b', s=6)
		plt.plot(mu_check_arr, vI(mu_check_arr), 'g--', label=lab % tuple(params))
		plt.title('I vs mu wl='+str(wl)+' T='+str(temp)+' g='+str(g))
		plt.xlabel('mu')
		plt.ylabel('intensity')
		plt.legend()
		fig.savefig('I_vs_mu_wl'+str(wl)+'T'+str(temp)+'g'+str(g)+'.png')