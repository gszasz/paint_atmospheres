import star.surface as sf
import star.map as mp
import util as ut
import math

class Star:
	""" Contains all the information pertaining to a rotating star, including its surface shape,
	a map of physical and geometrical features across its surface,
	its size, mass and luminosity. """
	def __init__(self, omega, inclination, luminosity, mass, Req, z_step, wl_arr, fit_params):
		self.luminosity = luminosity
		self.mass = mass
		self.Req = Req
		# information about the surface shape of the star
		self.surface = sf.Surface(omega, inclination)
		# an additive constant for log g and a multiplicative constant for Teff
		add_logg = math.log10(ut.G*ut.Msun/ut.Rsun**2) + math.log10(mass) - 2 * math.log10(Req)
		mult_temp = ut.Tsun * Req**(-0.5) * luminosity**(0.25)
		# map of gravity, temperature, intensity fit parameters 
		# and other features across the surface of the star
		self.map = mp.Map(self.surface, z_step, add_logg, mult_temp, wl_arr, fit_params)