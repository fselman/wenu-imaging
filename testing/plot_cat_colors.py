import pandas as pd
import matplotlib.pyplot as plt
import os

def determine_band(file_path):
    """
    Determine the band extracted in a *_clean.csv file
    """
    df = pd.read_csv(file_path)

    # raw_<band> it it exists or frame_ab_<band>
    bands = ['u_SDSS', 'g_SDSS', 'r_SDSS', 'i_SDSS', 'z_SDSS']

    band_raw = None
    for col in df.columns:
        if col.startswith('raw_ab_'):
            band_raw = col.split('raw_ab_')[1]
            if band_raw in bands:
                print(f"The band found is: {band_raw}")

    band_frame = None
    for col in df.columns:
        if col.startswith('frame_ab_'):
            band_frame = col.split('frame_ab_')[1]
            if band_frame in bands:
                print(f"The band found is: {band_frame}")

    if band_frame is not None and band_raw is not None and band_frame is band_raw:
        band = band_frame
        cal_mag = 'frame_ab_'+band
    elif band_frame is not None and band_raw is not None and band_frame is not band_raw:
        print(f"determine band: band_raw: {band_raw} differs from {band_frame}")
        return None, None
    elif band_frame is not None:
        band = band_frame
        cal_mag = 'frame_ab_'+band
    elif band_raw is not None:
        band = band_raw
        cal_mag = 'raw_ab_'+band
    else:
        print("determine_band: should never get here")
        return None, None

    return band, cal_mag

def determine_sides(band):
    """
    Returns de side band of band, and band2, and band3 to make
    the colour to plot agains, band2 - band3.
    """

    if 'u_SDSS' in band:
        side_band = 'g_SDSS'
        band2 = 'g_SDSS'
        band3 = 'r_SDSS'
    elif 'g_SDSS' in band:
        side_band = 'r_SDSS'
        band2 = 'r_SDSS'
        band3 = 'i_SDSS'
    elif 'r_SDSS' in band:
        side_band = 'i_SDSS'
        band2 = 'r_SDSS'
        band3 = 'z_SDSS'
    elif 'z_SDSS' in band:
        side_band = 'i_SDSS'
        band2 = 'r_SDSS'
        band3 = 'z_SDSS'
    elif 'g_psf' in band:
        side_band = 'r_psf'
        band2 = 'r_psf'
        band3 = 'i_psf'
    else:
        return None, None, None

    return side_band, band2, band3


# Function to read CSV and plot g-r vs r-i, coloring points by g_SDSS values
def plot_sdss_colors(file_path, plot_band=None,  limits='cat'):
    """
    Skymapper DR1: https://ui.adsabs.harvard.edu/abs/2018PASA...35...10W/abstract
    Skymapper DR2: https://ui.adsabs.harvard.edu/abs/2019PASA...36...33O/abstract
    Skymapper DR4: https://arxiv.org/abs/2402.02015
    """
    # Read the CSV file
    data = pd.read_csv(file_path)

    # If we do not pass a band name we assume that the file
    # is a clean file with an attached raw_ or frame_ab_ mag
    # column
    #
    if plot_band is None:
        band, cal_mag = determine_band(file_path)
        side_band, band2, band3 = determine_sides(band)
        if side_band is None or band2 is None or band3 is None:
            return None
    else:
        band = plot_band
        side_band, band2, band3 = determine_sides(band)
        cal_mag = None
        if side_band is None or band2 is None or band3 is None:
            return None

    # sort data by g_sdss
    data = data.sort_values(by=band, ascending=False)
   
    # Calculate g-r and r-i of the standard bands
    g_r = data[band] - data[side_band]
    r_i = data[band2] - data[band3]

    # Now we calculate the g_r for the calibrated band
    if cal_mag is not None:
        g_r_cal = data[cal_mag] - data[side_band]
   
    # Create the plot, color points based on g_SDSS values
    plt.figure(figsize=(8, 6))
    scatter = plt.scatter(g_r, r_i, c=data[band], cmap='plasma_r', label='std mags', s=15, alpha=0.8)
    xlim = plt.gca().get_xlim()
    ylim = plt.gca().get_ylim()
   
    # Set the title and labels with the file name
    plt.title(f'{band} - {side_band} vs {band2} - {band3} from {file_path}', fontsize=16)
    plt.xlabel(f'{band} - {side_band}', fontsize=16)
    plt.ylabel(f'{band2} - {band3}', fontsize=16)

    # wplot filtering by magnitude residual
    if cal_mag is not None:
        residual = data[cal_mag] - data[band]
        sel = abs(residual) < 500.
        scatter = plt.scatter(g_r_cal[sel], r_i[sel], label='cal mags', marker='+', s=10, color='k')
        if 'cat' in limits:
            plt.xlim(xlim)
            plt.ylim(ylim)
   
    # Set tick parameters
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
   
    # Add a colorbar to show the scale of g_SDSS values
    colorbar = plt.colorbar(scatter)
    colorbar.set_label(band, fontsize=16)
   
    # Show the plot
    plt.grid(True)
    plt.legend()
   
    # Save the plot as a PNG file
    output_file = os.path.splitext(file_path)[0] + '.png'
    plt.savefig(output_file)
    plt.show()

# Main entry point of the script
if __name__ == "__main__":
    # Example of using the function with an arbitrary file name
    file_path = 'sdss_query_result_M67_clean.csv'
    plot_sdss_colors(file_path, plot_band=None)
