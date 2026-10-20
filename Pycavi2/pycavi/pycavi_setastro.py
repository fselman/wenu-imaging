import os
import configparser
import os
import subprocess

def find_executables_which(possible_names):
    """Find all instances of an executable using 'which -a' for multiple possible names."""
    found_paths = []

    for name in possible_names:
        try:
            paths = subprocess.check_output(["which", "-a", name], text=True).strip().split("\n")
            found_paths.extend(paths)
        except subprocess.CalledProcessError:
            pass  # Ignore if command is not found

    return list(set(found_paths))  # Remove duplicates

def find_executables_in_roots(possible_names, root_dirs):
    """Recursively search for executables in multiple root directories."""
    found_paths = []

    for root in root_dirs:
        for dirpath, _, filenames in os.walk(root):
            for name in possible_names:
                if name in filenames:
                    full_path = os.path.join(dirpath, name)
                    found_paths.append(full_path)

    return list(set(found_paths))  # Remove duplicates

def find_and_choose_executables():
    """Finds astronomy-related executables, allows user to select a version, and saves paths in a config file."""
    executables = {
        "mefpp": ["mefpp"],
        "solve-field": ["solve-field"],
        "sextractor": ["sextractor", "source-extractor"],  # Check both names
        "scamp": ["scamp"],
        "swarp": ["swarp"]
    }

    # Define extra directories to search
    root_dirs = ["/usr/local", "/opt/local", "/home", "/Users", "/usr"]

    chosen_paths = {}

    for exe, possible_names in executables.items():
        # Search in system PATH using `which -a`
        found_paths = find_executables_which(possible_names)

        # Search in additional directories recursively
        found_paths.extend(find_executables_in_roots(possible_names, root_dirs))

        found_paths = list(set(found_paths))  # Remove duplicates

        if not found_paths:
            print(f"\n{exe}: NOT FOUND")
            chosen_paths[exe] = "NOT FOUND"
            continue
       
        # Display options
        print(f"\n{exe}: Multiple versions found:")
        for idx, path in enumerate(found_paths, 1):
            print(f"  {idx}) {path}")

        # Ask user to choose
        while True:
            try:
                choice = input(f"Choose the number for {exe} (or press Enter to select the first option): ")
                if choice == "":
                    chosen_paths[exe] = found_paths[0]  # Default to first option
                else:
                    chosen_paths[exe] = found_paths[int(choice) - 1]
                break
            except (ValueError, IndexError):
                print("Invalid choice. Please enter a valid number.")

    # Ensure the config directory exists
    config_dir = os.path.expanduser("~/.pycavi")
    os.makedirs(config_dir, exist_ok=True)

    # Write selected paths to config file
    config_file = os.path.join(config_dir, "pycavi_astrosoft.cfg")
    config = configparser.ConfigParser()
    config["Paths"] = chosen_paths

    with open(config_file, "w") as f:
        config.write(f)

    print(f"\nConfiguration file saved at: {config_file}")

# Run the function
if __name__ == "__main__":
    find_and_choose_executables()
