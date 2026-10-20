import numpy as np

def random_sampling_no_repeats(n, n_sel):
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

if __name__ == "__main__":
    # Define parameters
    n = 100   # The total number of elements
    n_sel = 10  # The number of elements to select per iteration

    # Run the sampling function
    sampling_results = random_sampling_no_repeats(n, n_sel)
    for atuple in sampling_results:
        print(atuple)

    # Display the results
    #for i, (selected, unselected) in enumerate(sampling_results):
        #print(f"Iteration {i+1}:")
        #print(f"Selected indices: {selected}")
        #print(f"Unselected indices: {unselected}")
        #print(f"Sum of elements: {len(selected) + len(unselected)}")
        #print("\n")
