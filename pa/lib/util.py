# Generally useful functions. Uses cgs units unless specified otherwise.
import math
import sys
import numpy as np
from scipy.interpolate import interp1d

### physical constants
Lsun = 3.839e33 # solar luminosity in erg/s
G = 6.674e-8 # gravitational constant in cm**3 g**-1 s**-2
Msun = 1.989e33 # mass of the sun in grams
Rsun = 6.9551e10 # solar radius in cm
sigma = 5.6704e-5 # Stefan-Boltzmann constant in erg*cm**-2*s**-1*K**-4
c = 2.99792458e10 # speed of light in cm/s
h = 6.62606885e-27 # planck's constant in erg*s
k = 1.3806504e-16 # Boltzmann constant in erg/K
D10 = 3.085678e+19 # ten parsecs in cm
Tsun = (Lsun / (4*math.pi*sigma*Rsun**2))**(0.25) # temperature of the sun in Kelvins
Zsun = 0.017 # from Grevesse, N., & Sauval, A. J., 1998, Space Sci. Rev., 85, 161 (used by Castelli and Kurucz 2004)

# printf() function from O'Reilly's Python Cookbook
def printf(format, *args):
    sys.stdout.write(format % args)

# inputs: starting and ending time in seconds
# output: a string with the time in hours, minutes and seconds
def timef(atime):
	hours, rem = divmod(atime, 3600)
	minutes, seconds = divmod(rem, 60)
	res = "{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds)
	return res

# pseudo effective temperature
def tau(L, Req):
	return ( L * Lsun / (4 * np.pi * sigma * (Req * Rsun)**2) )**(1./4)
# luminosity in solar luminosities
def L(tau, Req):
	return 4 * np.pi * (Req * Rsun)**2 * sigma * tau**4 / Lsun

# log pseudo effective gravity
def gamma(M, Req):
	return np.log10( G * M * Msun / (Req * Rsun)**2 )
# mass in solar masses
def M(gamma, Req):
	return 10**gamma * (Req * Rsun)**2 / (G * Msun)

# v sin i from mass
def vsini1(M, R, omega, inc):
	return omega * np.sqrt(G * M * Msun / (R * Rsun)) * np.sin(inc)
# v sin i from gamma
def vsini(gamma, R, omega, inc):
	return omega * np.sqrt(10**gamma * R * Rsun) * np.sin(inc) 

# refine a sorted 1-D grid by almost some factor n, keeping the original grid values:
# insert n-1 equally spaced values between every two neighbors;
# this makes a grid of size N_0 * n - (n - 1), where N_0 is the original grid size.
def refine(grid, factor):
	newgrid = np.array([])
	for i in range(len(grid) - 1):
		newgrid = np.append(newgrid, np.linspace(grid[i], grid[i + 1], factor + 1))
	newgrid = np.unique(newgrid)
	return newgrid

# approximate the bolometric luminosity of a star in erg/s/ster
# 	using the trapezoidal rule
# input: light from the star at many wavelengths in erg/s/ster/Hz
#	wavelengths in nm
def bolometric(light, wl):
	# convert intensity per Hz of frequency to per nm of wavelength 
	# this is the integrand in our integral w.r.t. wavelength
	f = ut.Hz_to_nm(light, wl)
	# calculate the differences between wavelengths in nm
	diff = np.diff(wl)
	## estimate the integral using the trapezoidal rule with variable argument differentials
	# array of averaged differentials
	d = 0.5 * ( np.append(diff, 0) + np.insert(diff, 0, 0) )
	return np.sum(d * f)

### Wavelength / frequency conversions

# inputs: an array of wavelengths in nanometers
# output: an array of frequencies in Hz
def color_nm_Hz(wl):
	c_nm = 1.e7 * c # speed of light in nm per second
	return c_nm / wl

### intensity / flux conversions

# inputs: an array of some quantity per Angstrom of wavelength, 
# 	an array of corresponding wavelengths in Angstroms
# output: an array of the same quantity per Hertz of frequency
def A_to_Hz(f_arr, wl_arr):
	cA = 1.e8 * c # speed of light in angstroms per second
	return f_arr * wl_arr**2 / cA

# inputs: an array of some quantity per Hz of frequency 
#	(last dimension is wavelength), 
# 	an array of corresponding wavelengths in nanometers
# output: an array of the same quantity per Angstrom of wavelength
def Hz_to_A(x, wl):
	cA = 1.e8 * c # speed of light in angstroms per second
	wl_A = 1.e1 * wl # wavelengths in angstroms
	return x * cA / wl_A**2

# inputs: an array of some quantity per nanometer of wavelength, 
# 	an array of corresponding wavelengths in nanometers
# output: an array of the same quantity per Hertz of frequency
def nm_to_Hz(f_arr, wl_arr):
	c_nm = 1.e7 * c # speed of light in nm per second
	return f_arr * wl_arr**2 / c_nm

# inputs: an array of some quantity per Hz of frequency, 
# 	an array of corresponding wavelengths in nanometers
# output: an array of the same quantity per nm of wavelength
def Hz_to_nm(f_arr, wl_arr):
	c_nm = 1.e7 * c # speed of light in nm per second
	return f_arr * c_nm / wl_arr**2

# integrate intensity (last dimension is wavelength) 
# convolved with the transmission curve and, optionally, the reddening curve, 
# normalize by the integral of the transmission curve
# Inputs: intensity array in ergs cm^-2 s^-1 Hz^-1 ster^-1 (wavelength dimension should be last)
#	intensity wavelengths in nm
# 	transmission curve 
#	filter wavelengths in nm
#	optional A_lambda reddening parameter at the light's wavelengths
# Output: intensities in erg cm^-2 s^-1 nm^-1 ster^-1, with the wavelength dimension filtered out
def filter(I, wll, trans, wlf, alam=0):
	# a cubic spline based on the filter
	Tfunc = interp1d(wlf, trans, kind='cubic', bounds_error=False, fill_value=0)
	# evaluate the transmission curve at the light's wavelengths
	T = Tfunc(wll)
	# convert intensity from per Hz to per nm
	I = Hz_to_nm(I, wll)
	# calculate the differences between light's wavelengths
	diff = np.diff(wll)
	## estimate the integral using the trapezoidal rule with variable argument differentials
	# array of averaged differentials
	d = 0.5 * ( np.append(diff, 0) + np.insert(diff, 0, 0) )
	# approximation of the integral, flux integrated over wavelengths
	intensity = np.sum( d * I * T * 10**(-alam/2.5), axis=-1 )
	# where intensity is not zero or nan, normalize by the integral of the transmission curve
	output = np.empty_like(intensity)
	mask = np.logical_or( intensity == 0, np.isnan(intensity) )
	output[ mask ] = intensity[ mask ]
	output[ ~mask ] = intensity[ ~mask ] / np.sum( d * T )
	return output

# Inputs: an array of wavelengths in angstroms
# 	optional R_V reddening parameter
# Result: A_lambda / A_V
# Based on: Fitzpatrick 1999, optical and infrared anchors from IDL astrolib
# Adapted from: f99.py
def alamv(lam, rv=3.1, model='f99'):

    x = 1.e4 / np.ravel(lam)

    # below 910 A, no light gets through;
    # above 6 microns, all the light gets through
    k = np.zeros_like(x)
    k[ x > 11. ] = np.inf
    uv_region = (1.e4 / 2700. <= x <= 11.)
    oir_region = (0.167 <= x < 1.e4 / 2700.)

    if np.any(x < 0.167) or np.any(x > 11.):
        raise ValueError('Wavelength(s) must be between 910 A and 6 um')
    if model == 'fm07' and abs(r_v - 3.1) > 0.001:
        raise ValueError('fm07 model not implementend for r_v != 3.1')
    if model != 'f99' and model != 'fm07':
        raise ValueError('Reddening model %s not implemented.' % (model))

    # UV region
    y = x[uv_region]
    if model == 'f99':
        x0, gamma = 4.596, 0.99
        c3, c4, c5 = 3.23, 0.41, 5.9
        c2 = -0.824 + 4.717 / r_v
        c1 = 2.030 - 3.007 * c2
        d = y**2 / ((y**2 - x0**2)**2 + y**2 * gamma**2)
        f = np.zeros_like(y)
        valid = (y >= c5)
        f[valid] = 0.5392 * (y[valid] - c5)**2 + 0.05644 * (y[valid] - c5)**3
        k_uv = c1 + c2 * y + c3 * d + c4 * f
    if model == 'fm07':
        x0, gamma = 4.592, 0.922
        c1, c2, c3, c4, c5 = -0.175, 0.807, 2.991, 0.319, 6.097
        D = y**2 / ((y**2-x0**2)**2 + y**2 * gamma**2)
        k_uv = np.zeros_like(y)
        valid = (y <= c5)
        k_uv[valid] = c1 + c2*y[valid] + c3*D[valid]
        valid = (y > c5)
        k_uv[valid] = c1 + c2*y[valid] + c3*D[valid] + c4*(y[valid] - c5)**2
    k[uv_region] = k_uv

    # Calculate values for UV spline points to anchor OIR fit
    x_uv_spline = 1.e4 / np.array([2700., 2600.])
    d = (x_uv_spline**2 /
         ((x_uv_spline**2 - x0**2)**2 + x_uv_spline**2 * gamma**2))
    k_uv_spline = c1 + c2 * x_uv_spline + c3 * d

    # Optical / IR region
    y = x[oir_region]
    if model == 'f99':
        anchors_x = 1.e4 / np.array([np.inf, 26500., 12200., 6000., 5470.,
                                     4670., 4110.])

        # The OIR anchors are from IDL astrolib, not F99.
        anchors_extinction = np.array(
            [0.,
             0.26469 * r_v / 3.1,  # IR
             0.82925 * r_v / 3.1,  # IR
             -0.422809 + 1.00270 * r_v + 2.13572e-04 * r_v**2,  # optical
             -5.13540e-02 + 1.00216 * r_v - 7.35778e-05 * r_v**2,
             0.700127 + 1.00184 * r_v - 3.32598e-05 * r_v**2,
             (1.19456 + 1.01707 * r_v - 5.46959e-03 * r_v**2 +
              7.97809e-04 * r_v**3 - 4.45636e-05 * r_v**4)]
            )

        anchors_x = np.append(anchors_x, x_uv_spline)
        anchors_k = np.append(anchors_extinction - r_v, k_uv_spline)

    oir_spline = interp1d(anchors_x, anchors_k, kind='cubic')
    k[oir_region] = oir_spline(y)

    return k / r_v + 1