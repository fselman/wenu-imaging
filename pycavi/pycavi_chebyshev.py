import logging

import numpy as np
from numpy.polynomial import chebyshev
from numpy.polynomial.chebyshev import chebvander2d
import pandas as pd
import sympy

def fit_chebyshev(x, y, z, z_err, dimx, dimy, deg):
    """
    Fits a chebyshev polynomial using the numpy.linalg.lstsq
    procedure via Vandermonde matrices with chebvander2d.

    Input
    =====

        x:     [float] The x-ccordinates [pix] of the sampled points
        y:     [float] The y-coordinates [pix] of the sampled points
        z:     [float] Value at point x, y
        z_err: [float] 1-sigma uncertainty in the value at point x, y
        dimx:  [int] Image dimension x
        dimy:  [int] Image dimension y
        deg:   [int tuple)]degrees of polynomials in x, y

    filter_data should be called before this routine.

    """

    # Construct the Chebyshev design matrix for 2D data
    x_scaled, y_scaled = pixel_coords_scaled(x, y, dimx, dimy)
    V = chebvander2d(x_scaled, y_scaled, deg)

    # Apply weights
    W = np.diag(1 / z_err)  # Weight matrix (inverse of errors)
    VW = W @ V  # Weighted design matrix
    zW = W @ z  # Weighted z values

    # Solve the weighted least squares problem
    coefficients, residuals, rank, s = np.linalg.lstsq(VW, zW, rcond=None)

    # We fit the masked values and correct the magnitudes
    z_corr = z - chebyshev_2d_eval(x, y, dimx, dimy, coefficients, deg)

    return z_corr, coefficients, residuals, rank, s

# Evaluate the fitted polynomial at new points
def chebyshev_2d_eval(x_pix, y_pix, dimx, dimy, coeff, deg):
    """
    Evaluate the Chebyshev polynomial at the points defined
    by the 1d ndarrays x and y. Note that x and y should be
    scaled to lie in the interval -1 to 1.
    """
    # Generate 2D Vandermonde matrix for new points
    # For well behaved polynomials we need to rescale coordinates to [-1, 1]
    # Needs to rescale the x and y values before fitting the Chebyshev polys
    x, y = pixel_coords_scaled(x_pix, y_pix, dimx, dimy)
    V_new = chebvander2d(x, y, deg)
    return np.dot(V_new, coeff)


def pixel_coords_scaled(xcoord, ycoord, dimx, dimy):
    """
    Converts pixel coordinates and scale them to the intervale [-1, 1].
    """
    x_scaled = 2 * (xcoord - dimx/2) / dimx
    y_scaled = 2 * (ycoord - dimy/2) / dimy
    return x_scaled, y_scaled

def chebyshev_polynomials( deg, coefficients=None, coeff_file=None, origfile=None, dimx=None, dimy=None):
    """
    Print the Chebyshev polynomials from the coefficients.

    Parameters:

    - deg:          degree of polynomial
    - coefficients: 2D array of Chebyshev coefficients.
    - coeff_file:   full path to file to store coefficients and polynomials
    - dimx, dimy:   dimesion of image for the polynomial approx.

    """
    def cheb2std_nozeros(cheb_poly, new_var_name='x'):
        """
        Convert a Chebyshev polynomial to its standard polynomial form,
        replace the variable name, and eliminate zero coefficient terms.
        
        Parameters:
        - cheb_poly: Chebyshev polynomial object (numpy.polynomial.Chebyshev).
        - new_var_name: String, new variable name to use in the output.
        
        Returns:
        - poly_str: String representation of the standard polynomial with zero terms removed.
        """
        # Convert the Chebyshev polynomial to standard polynomial form
        standard_poly = cheb_poly.convert(kind=np.polynomial.Polynomial)
    
        # Extract coefficients and corresponding terms
        coeffs = standard_poly.coef
        terms = []

        # Construct polynomial terms, omitting zero coefficients
        for power, coeff in enumerate(coeffs):
            if coeff != 0.0:
                if power == 0:
                    terms.append(f"{coeff:.0f}")
                elif power == 1:
                    terms.append(f"{coeff:.0f} * {new_var_name}")
                else:
                    terms.append(f"{coeff:.0f} * {new_var_name}^{power}")

        # Combine all terms into the final polynomial string
        poly_str = " + ".join(terms).replace('^', '**')

        return poly_str

    num_x, num_y = deg[0], deg[1]
    if coeff_file is not None:
        with open(coeff_file, 'w') as f:
            f.write(f"# 2D Chebyshev polynomial in x and y\n")
            f.write(f"# ORIGFILE: {origfile}\n")
            f.write(f"# x_deg: {deg[0]}\n")
            f.write(f"# y_deg: {deg[1]}\n")
            f.write(f"# dimx: {dimx}\n")
            f.write(f"# dimy: {dimy}\n")
            f.write("# x = 2 * (x_pix - dimx/2) / dimx\n")
            f.write("# y = 2 * (y_pix - dimy/2) / dimy\n")


    if coefficients is not None:
        coefficients = coefficients.reshape(deg[0]+1, deg[1]+1)
        logging.info("coefficients.shape: {}".format(coefficients.shape))

        # I save the explicit form of the polynomial to write it in the headers
        # of the image, eventually.
        #
        ncount = 0
        cheb_coeff = {}
        cheb_poly2d = {}
        for i in range(num_x):
            for j in range(num_y):
                ncount+=1
                coeff = coefficients[i, j]
                cheb_coeff[(i,j)] = coeff
                if coeff != 0:
                    poly_x = chebyshev.Chebyshev([0] * i + [1])
                    poly_y = chebyshev.Chebyshev([0] * j + [1])
                    cheb_poly2d[(i,j)] = f"T_{i}(x) * T_{j}(y)"
                    logging.info(f"{ncount:02d} Coefficient({i}, {j}): {coeff:.8f} * T_{i}(x) * T_{j}(y)")
                    if coeff_file is not None:
                        with open(coeff_file, 'a') as f:
                            f.write(f"{i}, {j}, {cheb_poly2d[(i,j)]}, {cheb_coeff[(i,j)]}\n")

    cheb_poly_x = {}
    cheb_poly_x_str = {}
    for i in range(num_x):
        poly_x = chebyshev.Chebyshev([0] * i + [1])
        cheb_poly_x[i] = poly_x
        cheb_poly_x_str[i] = f"{cheb2std_nozeros(poly_x)}"
        logging.info(f"T_{i}(x): {cheb2std_nozeros(poly_x)}")
        if coeff_file is not None:
            with open(coeff_file, 'a') as f:
                f.write(f"x {i}: T_{i}(x) = {cheb_poly_x_str[i]}\n")

    cheb_poly_y = {}
    cheb_poly_y_str = {}
    for j in range(num_y):
        poly_y = chebyshev.Chebyshev([0] * j + [1])
        cheb_poly_y[j] = poly_y
        cheb_poly_y_str[j] = f"{cheb2std_nozeros(poly_y, new_var_name='y')}"
        logging.info(f"T_{j}(y): {cheb2std_nozeros(poly_y, new_var_name='y')}")
        if coeff_file is not None:
            with open(coeff_file, 'a') as f:
                f.write(f"y {j}: T_{j}(y) = {cheb_poly_y_str[j]}\n")

    return coefficients, cheb_poly_x_str, cheb_poly_y_str

def evaluate_2dpoly(x_pix, y_pix, dimx, dimy, deg, poly_x_strlst, poly_y_strlst, coefficients):
    """
    Evaluate polynomial 

    2dpoly(x, y) = Sum_i_j coeffs(i, j)*poly_x(i, x)*poly_y(j, y)

    These polynomials will go in the headers of the images so we
    work with them in the illumination correction to ensure that
    they work.

    Parameters

    x_pix, y_pix:   ndarrays of pixel coordinates of point of evaluation
    dimx, dimy:     dimensions of image
    deg:            tuple giving the degree of the polynomial
    poly_x_strlst:  list of strings with the polynomial basis in x
    poly_y_strlst:  list of strings with the polynomial basis in y
    coefs:          dictionary with coefficients indexe by i, j

    Output

        The value of the polynomial evaluated in the points defined
        bu arrays x, y.
    """

    num_x, num_y = deg[0], deg[1]

    # scale to -1, 1 both input coordinate arrays
    x_scaled, y_scaled = pixel_coords_scaled(x_pix, y_pix, dimx, dimy)

    # prepare sympy
    #x, y = sympy.symbols('x y')
    #y = sympy.symbols('y')

    x = sympy.symbols('x')
    poly_x = {}
    for i in range(num_x):
        poly_x[i] = sympy.lambdify(x, poly_x_strlst[i], modules='numpy')

    y = sympy.symbols('y')
    poly_y = {}
    for j in range(num_y):
        poly_y[j] = sympy.lambdify(y, poly_y_strlst[j], modules='numpy')

    value = np.full_like(x_scaled, 0.0, dtype=np.float64)
    for i in range(num_x):
        for j in range(num_y):
            value = value + coefficients[i, j]*poly_x[i](x_scaled)*poly_y[j](y_scaled)

    return value

def append_hashline(filename, new_header_line):
    # Open the file and read all lines
    with open(filename, 'r') as file:
        lines = file.readlines()

    # Find the position of the last header line (lines starting with '#')
    header_end = 0
    for i, line in enumerate(lines):
        if line.startswith('#'):
            header_end = i

    # Insert the new header line after the last header line
    lines.insert(header_end + 1, new_header_line + '\n')

    # Write the modified content back to the file (or to a new file)
    with open(filename, 'w') as file:
        file.writelines(lines)

def parse_cheb_file(file_content):
    """
    Procedure that loads coefficients and 1D polynomials for
    a 2D representation of a Chebyshev polynomial stored
    in a file and returns  dictionary. Can be used as part of
    a separate procedure to correct photometry in a catalogue
    extracted from the FITS image used to determine the
    illumination corrections.
    """
    # Dictionary to store the parsed data
    parsed_data = {
        'x_deg': None,
        'y_deg': None,
        'dimx': None,
        'dimy': None,
        'polynomials_x': {},  # Polynomials for T_i(x)
        'polynomials_y': {},  # Polynomials for T_j(y)
        'coefficients': {}  # Coefficients c(I, j) as a dictionary with keys (I, j)
    }

    # Split the file content into lines
    with open(file_content, 'r') as f:
        lines = [line for line in f]

    for line in lines:
        line = line.strip()
        if not line or 'pix' in line or 'Chebyshev' in line:
            continue  # Skip empty lines or not relevant lines

        # We first parse the headers of the file to
        # handle the variables: x_deg, y_deg, dimx, dimy
        if 'ORIGFILE' in line:
            parsed_data['origfile'] = line.split('ORIGFILE:')[-1].strip()
        elif "x_deg" in line:
            parsed_data['x_deg'] = int(line.split('x_deg:')[-1].strip())
        elif "y_deg" in line:
            parsed_data['y_deg'] = int(line.split('y_deg:')[-1].strip())
        elif "dimx" in line:
            parsed_data['dimx'] = int(line.split('dimx:')[-1].strip())
        elif "dimy" in line:
            parsed_data['dimy'] = int(line.split('dimy:')[-1].strip())

        if line.startswith("#"):
            continue

        # Handle polynomial definitions like: x 0: T_0(x) = 1
        elif "x" == line[0] and  "T_" in line and "(x)" in line:
            parts = line.split(':')
            index = int(parts[0].split()[1])
            polynomial = parts[1].split('=')[-1].strip()
            parsed_data['polynomials_x'][index] = polynomial

        elif "y" == line[0] and  "T_" in line and "(y)" in line:
            parts = line.split(':')
            index = int(parts[0].split()[1])
            polynomial = parts[1].split('=')[-1].strip()
            parsed_data['polynomials_y'][index] = polynomial

        # Handle coefficients like: 0, 0, T_0(x) * T_0(y), 0.02912866079326984
        elif "," in line:
            parts = line.split(',')
            i = int(parts[0].strip())
            j = int(parts[1].strip())
            coefficient = float(parts[3].strip())
            parsed_data['coefficients'][(i, j)] = coefficient

    return parsed_data
