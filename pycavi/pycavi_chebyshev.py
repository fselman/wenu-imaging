import logging
import numpy as np
from numpy.polynomial import chebyshev
from numpy.polynomial.chebyshev import chebvander2d
import pandas as pd

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
    x_scaled, y_scaled = self.pixel_coords_scaled(x, y, dimx, dimy)
    V = chebvander2d(x_scaled, y_scaled, deg)

    # Apply weights
    W = np.diag(1 / z_err)  # Weight matrix (inverse of errors)
    VW = W @ V  # Weighted design matrix
    zW = W @ z  # Weighted z values

    # Solve the weighted least squares problem
    coefficients, residuals, rank, s = np.linalg.lstsq(VW, zW, rcond=None)

    # We fit the masked values and correct the magnitudes
    z_corr = z - chebyshev_2d_eval(x, y, coefficients, deg)

    return z_corr, coefficients, residuals, rank, s

# Evaluate the fitted polynomial at new points
def chebyshev_2d_eval(self, x_pix, y_pix, coeff, deg):
    """
    Evaluate the Chebyshev polynomial at the points defined
    by the 1d ndarrays x and y. Note that x and y should be
    scaled to lie in the interval -1 to 1.
    """
    # Generate 2D Vandermonde matrix for new points
    # For well behaved polynomials we need to rescale coordinates to [-1, 1]
    # Needs to rescale the x and y values before fitting the Chebyshev polys
    x, y = pixel_coords_scaled(x_pix, y_pix)
    V_new = chebvander2d(x, y, deg)
    return np.dot(V_new, coef)


def pixel_coords_scaled(xcoord, ycoord, dimx, dimy):
    """
    Converts pixel coordinates and scale them to the intervale [-1, 1].
    """
    x_scaled = 2 * (xcoord - dimx) / dimx + 1
    y_scaled = 2 * (ycoord - dimy) / dimy + 1
    return x_scaled, y_scaled

def print_chebyshev_polynomials( deg, coefficients=None):
    """
    Print the Chebyshev polynomials from the coefficients.

    Parameters:
    - coefficients: 2D array of Chebyshev coefficients.
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

    cheb_poly_x = {}
    cheb_poly_x_str = {}
    for i in range(num_x):
        poly_x = chebyshev.Chebyshev([0] * i + [1])
        cheb_poly_x[i] = poly_x
        cheb_poly_x_str[i] = f"{cheb2std_nozeros(poly_x)}"
        logging.info(f"T_{i}(x): {cheb2std_nozeros(poly_x)}")

    cheb_poly_y = {}
    cheb_poly_y_str = {}
    for j in range(num_y):
        poly_y = chebyshev.Chebyshev([0] * j + [1])
        cheb_poly_y[i] = poly_y
        cheb_poly_y_str[i] = f"{cheb2std_nozeros(poly_y)}"
        logging.info(f"T_{j}(y): {cheb2std_nozeros(poly_y, new_var_name='y')}")
        
if __name__ == "__main__":
    log_file_swarp = "./pycavi_chebyshev_main.log"
    logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s:%(levelname)s:%(message)s",
                    handlers=[
                              logging.FileHandler(log_file_swarp),
                              logging.StreamHandler()])
    logging.getLogger().setLevel(logging.INFO)

    print_chebyshev_polynomials((5,5))
