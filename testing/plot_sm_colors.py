import pandas as pd
import matplotlib.pyplot as plt
import os

# Function to read CSV and plot g-r vs r-i, coloring points by g_SDSS values
def plot_sdss_colors(file_path):
    # Read the CSV file
    data = pd.read_csv(file_path)

    # sort data by g_sdss
    data = data.sort_values(by='g_SDSS', ascending=False)
   
    # Calculate g-r and r-i
    g_r = data['g_SDSS'] - data['r_SDSS']
    r_i = data['r_SDSS'] - data['i_SDSS']
   
    # Create the plot, color points based on g_SDSS values
    plt.figure(figsize=(8, 6))
    scatter = plt.scatter(g_r, r_i, c=data['g_SDSS'], cmap='plasma_r', label='g-r vs r-i', s=3, alpha=0.8)
   
    # Set the title and labels with the file name
    plt.title(f'g-r vs r-i from {file_path}', fontsize=16)
    plt.xlabel('g - r', fontsize=16)
    plt.ylabel('r - i', fontsize=16)
   
    # Set tick parameters
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
   
    # Add a colorbar to show the scale of g_SDSS values
    colorbar = plt.colorbar(scatter)
    colorbar.set_label('g_SDSS', fontsize=16)
   
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
    file_path = 'sm_qry_M67_clean.csv'
    plot_sdss_colors(file_path)
