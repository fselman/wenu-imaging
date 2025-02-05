import os
import logging

from datetime import datetime

import numpy as np
import matplotlib.pyplot as plt

from astropy.io import fits

from pykrige.uk import UniversalKriging  # Ordinary Kriging from pykrige

from lmfit import Model
from scipy.optimize import curve_fit
from scipy.interpolate import RegularGridInterpolator
from scipy.spatial.distance import pdist

def random_sampling_no_repeats(n, n_sel):
    """
    Creates a series of indices arrays of length n_sel
    randomly selected from n.
    """
    # Create an array of consecutive integers from 0 to n
    arr = np.arange(n+1)

    # List to store all selected indices over iterations
    selected_history = set()

    # List to store the results
    results = []

    # Loop until all indices have been selected at least once
    while len(selected_history) < (n + 1):
        # Determine the indices that are still available to be selected (not in selected_history)
        available_indices = np.setdiff1d(arr, list(selected_history))

        # Randomly select n_sel indices from available indices without replacement
        n_sel_actual = min(n_sel, len(available_indices))  # Adjust in case fewer indices remain
        selected_indices = np.random.choice(available_indices, size=n_sel_actual, replace=False)

        # Add the selected indices to the history set
        selected_history.update(selected_indices)

        # The remaining unselected indices are the complement of the selected ones
        unselected_indices = np.setdiff1d(arr, selected_indices)

        # Append the tuple of selected and unselected arrays
        results.append((selected_indices, unselected_indices))

    return results

# Use a call to uk to determine parameters
def kriging_interpolation(x_subset, y_subset, z_subset, 
                init_kriging = True, 
                selected_model = 'gaussian', 
                maxlag = 12000, 
                nlags = 200, 
                determine_empirical_variogram = True, 
                plot_variogram = False,
                use_empirical_variogram = False,
                fit_type = 'curve_fit',
                fixed_nugget = None,                        # if this value is none the nugget will also be fitted
                image_path=None):
    """
    Determine universal kriging interpolator using z values on a
    set of points.

    Parameters

        x_subset, y_subset, z_subset:    Values with 2D pixel coordinates
        init_kriging:                    Do an initial run of UniversalKriging with default variogram
        selected_model:                  Which model to use ['gaussian'] 'exponential', 'spherical'
        maxlag:                          Maximum lag to use in fit. Tipically half the size of smallest axis
                                         to avoid edge effects
        nlags:                           Number of bins. Optimal value depends on number of input points.
        determine_empirical_variogram:   Flag to instruct the determination of an empirical variogram
        plot_variogram:                  Instruct to plot the empirical variogram
        use_empirical_variogram:         Flag to instruct to use the empirical variogram to fit the model,
                                         and pass these model parameters to UK.
        fit_type:                        curve_fit or lmfit.Model, this last one allows to fix the nugget
        fixed_nugget:                    if not None the value will be fixed during the fit and fit_type will be lmfit.Model

    Output

        UK:                              An instance of pykrige UniversalKriging object
        
    """
    
    if determine_empirical_variogram:
        # Combine x and y into a 2D array
        coordinates = np.column_stack((x_subset, y_subset))

        # Step 1: Calculate the pairwise distances between all points
        distances = pdist(coordinates)

        # ERASE
        # Convert to a square distance matrix
        #dist_matrix = squareform(distances)

        # Step 2: Calculate the empirical variogram
        def empirical_variogram(lags, values, bins):
            ''' Calculate empirical variogram for given lags and z-values (values) '''
            semivariance = np.zeros(len(bins) - 1)

            # Calculate the pairwise differences for the z values
            pairwise_diffs = pdist(values.reshape(-1, 1))**2  # Squared differences in z values

            # For each bin, compute the mean semivariance
            for i in range(len(bins) - 1):
                in_bin = np.logical_and(lags >= bins[i], lags < bins[i + 1])
                if np.sum(in_bin) > 0:
                    semivariance[i] = np.mean(pairwise_diffs[in_bin])
            return semivariance

        # Calculate lags and bins
        edists = pdist(coordinates)
        ebins = np.linspace(0, np.max(edists), nlags)
        esemivariance = 0.5*empirical_variogram(edists, z_subset, ebins)
        elags = ebins[:-1]
        print(f"edists.shape: {edists.shape}  elags.shape: {elags.shape}  esemivariance.shape: {esemivariance.shape}")


    # Interpolate onto the grid
    # Here I add new code
    # Define the grid size
    #n_pts = 50
    #gridx = np.linspace(1, zpcal.naxis1, n_pts)
    #gridy = np.linspace(1, zpcal.naxis2, n_pts)

    # Kriging model construction
    if init_kriging:
        UK = UniversalKriging(
            x_subset, y_subset, z_subset,
            variogram_model=selected_model,
            verbose=True,
            nlags=nlags,
            enable_plotting=False
        )

        # the parameters
        fitted_variogram_parameters = UK.variogram_model_parameters
        print(f"Fitted variogram parameters: {fitted_variogram_parameters}\n")

        # the variogram
        uk_lags = UK.lags
        uk_semivariance = UK.semivariance
        uk_model_values = UK.variogram_function(fitted_variogram_parameters, uk_lags)

    # Chose which variogram to use
    if use_empirical_variogram:
        elags = ebins[:-1]
        valid_idx = elags <= maxlag
        lags_truncated = elags[valid_idx]
        semivariance_truncated = esemivariance[valid_idx]
    else:
        valid_idx = uk_lags <= maxlag
        lags_truncated = uk_lags[valid_idx]
        semivariance_truncated = uk_semivariance[valid_idx]
        uk_model_values_truncated = UK.variogram_function(fitted_variogram_parameters, lags_truncated)

    # Step 3: Define the  variogram model functions
    # xponential, gaussian, and spherical variogram model
    #

    def exponential_variogram(h, nugget, partial_sill, range_):
        return nugget + partial_sill * (1 - np.exp(-h / range_))

    def gaussian_variogram(h, nugget, partial_sill, range_):
        return nugget + partial_sill * (1 - np.exp(-h**2 / range_**2))

    def spherical_variogram(h, nugget, partial_sill, range_, ):
        return np.where(
            h <= range_,
            nugget + partial_sill * (1.5 * (h / range_) - 0.5 * (h / range_)**3),
            nugget + partial_sill
        )
    model_function = {'exponential': exponential_variogram,
                      'gaussian': gaussian_variogram,
                      'spherical': spherical_variogram}
    # Select the model
    model = model_function[selected_model]
    
    # Step 4: Fit the model to the empirical variogram using curve_fit
    # Use initial guesses for nugget, sill, and range
    initial_guess = [0.1,0.1, 500.0]

    # Perform the fitting
    if 'curve_fit' in  fit_type and fixed_nugget is None:
        # Step 4: Fit the model to the empirical variogram using curve_fit
        # Use initial guesses for nugget, sill, and range
        initial_guess = [0.1,0.1, 500.0]
        # It is important to look at the nugget which has a tendency to be too close
        # to zero. If this is the case, do not hesitate to refit fixing this value
        # to a reasonable one, otherwise short range correlations will dominate.
        # CURRENTLY WE DO NOT PROVIDE THIS OPTION.
        #
        bounds=[(0, 0, 100.),(np.inf, np.inf, 5000.)]
        popt, pcov = curve_fit(model, lags_truncated, semivariance_truncated, p0=initial_guess, bounds=bounds)

        # Extract the fitted parameters
        fitted_nugget, fitted_partial_sill, fitted_range = popt
        variogram_parameters = {'psill': fitted_partial_sill, 'range': fitted_range, 'nugget': fitted_nugget}     # NB THE ORDER IS DIFFERENT
        print(variogram_parameters)
        print(f"Fitted Nugget: {fitted_nugget}, Partial Sill: {fitted_partial_sill}, Range: {fitted_range}")
    elif 'lmfit' in fit_type or fixed_nugget is not None:
        lmfit_model = Model(model)
        # Create parameters object and set initial values
        lmfit_params = lmfit_model.make_params(nugget=0.1, partial_sill=0.1 , range_=500)
        if fixed_nugget is not None:
            lmfit_params['nugget'].set(value=fixed_nugget, vary=False)

        lmfit_result = lmfit_model.fit(semivariance_truncated, lmfit_params, h=lags_truncated)
        fitted_nugget = lmfit_result.params['nugget'].value
        fitted_partial_sill = lmfit_result.params['partial_sill'].value
        fitted_range = lmfit_result.params['range_'].value
        variogram_parameters = {'psill': fitted_partial_sill, 'range': fitted_range, 'nugget': fitted_nugget}     # NB THE ORDER IS DIFFERENT
        popt = fitted_nugget, fitted_partial_sill, fitted_range
        print(variogram_parameters)
        print(f"Fitted Nugget: {fitted_nugget}, Partial Sill: {fitted_partial_sill}, Range: {fitted_range}")
    else:
        raise Exception(f"Inconsistent fit_type: {fit_type} and fixed_nugget: {fixed_nugget} values.")
        

    if plot_variogram:
        if image_path is not None:
            image_dir = os.path.dirname(image_path)
            image_name = os.path.basename(image_path)     # Note that it assumes that the extension have been stripped before the call
        save_file_name = f"{image_dir}/{image_name}_variogram_{selected_model}_{nlags}_{maxlag}_{round(fitted_nugget, 5)}.png"
        plt.figure(figsize=(8, 5))
        plt.suptitle(f"{image_name} variogram {selected_model} nlags: {nlags} maxlag: {maxlag} nugget: {round(fitted_nugget, 5)}")

        # Plot empirical variogram
        plt.scatter(lags_truncated, semivariance_truncated, color='blue', label='Empirical Variogram Truncated')
        plt.scatter(elags, esemivariance, color='green', marker='+', s=5, label='Full Empirical Variogram')

        # Plot model-fitted variogram
        plt.plot(elags, model_function[selected_model](elags, *popt), color='red', label='Fitted Variogram Model')
        plt.plot([0], [fitted_nugget], color='gold', marker='o')

        plt.xlabel('Lag Distance')
        plt.ylabel('Semivariance')
        plt.title(f"Empirical Variogram and Fitted Model {selected_model}")
        plt.legend()
        if image_name is not None:
            logging.info(f"Saving variogram in {save_file_name}")
            plt.savefig(save_file_name)
        plt.show()


    # Now we run for a second time UK but this time with the selected model and parameters
    UK = UniversalKriging(
        x_subset, y_subset, z_subset,
        variogram_model=selected_model,
        variogram_parameters = variogram_parameters,
        verbose=True,
        enable_plotting=False
    )

    return UK

def determine_kriging_errors(x, y, z, 
                             k=10,
                             init_kriging=True, 
                             selected_model='gaussian', 
                             maxlag=1, 
                             nlags=6, 
                             determine_empirical_variogram=True, 
                             plot_variogram=False, 
                             use_empirical_variogram=True,
                             fit_type = 'curve_fit',
                             fixed_nugget = None):
    """
    k-fold cross-validation procedure
    
    Does repeated kriging interpolations selecting a subset of A% points for checking errors
    and (100-A)% to carry out the interpolation. The number of runs is equal to 100/A

    Parameters

        x, y, z:          Positions and values of points to determine kriging
        k:                Percent of points to use for checking errors
        kargs:            Same as in procedure kriging_interpolation

    Output

        x_check, y_check, z_check, z_corr: Arrays with same dimensions as x, y, z with the corrected
                                           values in the interpolation.
    """
    # we loop over a whole set of random samplings of points to determine
    # error estimates.
    # Percentage k (e.g., 40% would be k = 40)
    num_check = int(len(x) * k / 100)                # Calculate how many elements correspond to k%
    logging.info(f"num_check: {num_check}    len(x): {len(x)}")

    # we produce sets of n-num_check random indices for interpolations and num_check for error determinations
    # in total sum(num_check) = n
    #
    idx_tuple_arrays = random_sampling_no_repeats(len(x)-1, num_check)    # this return a list of pairs of index arrays
    x_check = []
    y_check = []
    z_check = []
    z_corr = []
    for atuple in idx_tuple_arrays:
        logging.info(f"len(atuple[0]): {len(atuple[0])}    len(atuple[1]): {len(atuple[1])}")
        x_check_i = x[atuple[0]]
        y_check_i = y[atuple[0]]
        z_check_i = z[atuple[0]]
        x_subset_i = x[atuple[1]]
        y_subset_i = y[atuple[1]]
        z_subset_i = z[atuple[1]]

        plot_variogram = False
        UK = kriging_interpolation(x_subset_i, y_subset_i, z_subset_i, 
                    init_kriging = init_kriging, 
                    selected_model = selected_model, 
                    maxlag = maxlag, 
                    nlags = nlags, 
                    determine_empirical_variogram = determine_empirical_variogram, 
                    plot_variogram = plot_variogram,
                    use_empirical_variogram = determine_empirical_variogram,
                    fit_type = fit_type,
                    fixed_nugget = fixed_nugget,
                    image_path=None)
        dpix = 1
        corr, _ = UK.execute('points', x_check_i, y_check_i)
        z_corr_i = z_check_i - corr

        x_check.append(x_check_i)
        y_check.append(y_check_i)
        z_check.append(z_check_i)
        z_corr.append(z_corr_i)
    # Now we have a full set of check points evaluated
    # independently of the Kriging interpolation
    #
    x_check = np.concatenate(x_check)
    y_check = np.concatenate(y_check)
    z_check = np.concatenate(z_check)
    z_corr = np.concatenate(z_corr)

    return x_check, y_check, z_check, z_corr

# SAVING THE KRIGING MODEL
#
# We save an interpolated grid
#
def save_kriging_model(z_on_grid, npts,  header_dict, file_name):
    """
    Procedure to save the result of the interpolation. It will be saved 
    as a gridata image that can be used later to interpolate the values.

    The image z_on_grid of dimensions (n_pts, n_pts) was displayed with the command

    img = ax.imshow(z_on_grid, extent=(1, dimx, 1, dimy), origin='lower', cmap='viridis')

    """
    # Create a FITS header
    header = fits.Header()

    # Add custom keywords
    for akey, avalue in header_dict.items():
        header[akey] = avalue

    # and finally we add the ORIGFILE key with the ISO 8601 date format.
    now = datetime.now()
    formatted_date = now.strftime("%Y-%m-%dT%H:%S.%f")[:-3] # ISO 8601 truncated to millisecond
    origfile = "APDP."+formatted_date+".fits"   # Auxiliary Pycavi Data product
    header["ORIGFILE"] = (origfile, 'Unique name for this file')

    # Create the PrimaryHDU with the data and header
    hdu = fits.PrimaryHDU(data=z_on_grid.filled(np.nan), header=header)

    # Save the subsampled Kriging data to a FITS file with custom headers
    hdu.writeto(file_name, overwrite=True)

def get_kriging_interpolation(kriging_fits_name, x_pix, y_pix):
    """
    This procedure returns the interpolated values from a grid
    that was created using kriging.
    """

    # Load the FITS file with the metadata
    with fits.open(kriging_fits_name) as hdul:
        subsampled_kriging = hdul[0].data
        header = hdul[0].header

    # Extract metadata from the header
    original_height = header['ORIG_H']
    original_width = header['ORIG_W']
    factor = header['FACTOR']
    variogram_model = header['VARIOMOD']

    # If Kriging parameters are included in the header
    nugget = header.get('NUGGET', None)  # Use None if not present
    psill = header.get('PSILL', None)
    range_val = header.get('RANGE', None)

    # Define the subsampled grid based on the original size and factor
    x_subsampled = np.linspace(0, header['NAXIS1'], header['NAXIS1'])
    y_subsampled = np.linspace(0, header['NAXIS2'], header['NAXIS2'])

    # Define the extent for the subsampled image as if it covers the full original image size
    extent = [1, original_width, 1, original_height]

    # Set up an interpolator using the subsampled Kriging data
    # print(original_height, x_subsampled.shape, original_width, y_subsampled.shape, factor, subsampled_kriging.shape)
    interpolator = RegularGridInterpolator((y_subsampled, x_subsampled), subsampled_kriging, method='linear')

    # Function to map coordinates from original image space to the subsampled grid
    def get_values(x, y, extent, interp):
        # Unpack the extent (xmin, xmax, ymin, ymax)
        xmin, xmax, ymin, ymax = extent
    
        # Scale x and y to the subsampled grid
        scaled_x = (x - xmin) / (xmax - xmin) * (len(x_subsampled) - 1)
        scaled_y = (y - ymin) / (ymax - ymin) * (len(y_subsampled) - 1)

        return interp((scaled_y, scaled_x))

    # Retrieve the interpolated value
    gridx = np.linspace(1, original_width, factor)
    gridy = np.linspace(1, original_height, factor)
    grid_x, grid_y = np.meshgrid(gridx, gridy)
    return get_values(x_pix, y_pix, extent, interpolator), grid_x, grid_y,  subsampled_kriging, header


