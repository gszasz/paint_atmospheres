<img src="logo.png" width="20%">

# Paint the Atmospheres of Rotating Stars

Authors: 
	Timothy D. Brandt
	Mikhail Lipatov

Model: 
	Roche model of mass distribution, 
	solid body rotation,
	energy flux collinear with effective gravity.

Features:
	a closed-form expression for the azimuthal integral,
	a high-order approximation of the longitudinal integral,
	a precise calculation of surface effective temperature.

Installation (Unix):
	git clone https://github.com/mlipatov/paint_atmospheres
	cd paint_atmospheres
	pip install .
	# put a .pck file in ./data

Executables:
	calc_limbdark computes fits of intensity w.r.t surface inclination
	calc_star performs inclination-independent computations
	calc_spectra computes spectra for multiple inclinations
	<command> -h provides usage instructions

Scripts:
	Located in paint_atmospheres/pa/usr
	Create Figures 3-10 in [LB] and other figures
	Each contains instructions in the comments at the top of the file 

References: 
	Lipatov M & Brandt TD, Submitted to ApJ [LB]
	Espinosa Lara F & Rieutord M (2011), A&A, 533, A43
	Castelli F & Kurucz RL (2004), arXiv:astro-ph/0405087 
	http://mathworld.wolfram.com/CubicFormula.html
	Wikipedia:Bilinear interpolation:Algorithm
	Wikipedia:Newton's method
	Press WH et al, Numerical Recipes, 3rd ed. (2007) 
