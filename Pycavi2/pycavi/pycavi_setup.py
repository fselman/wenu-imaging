import os
import shutil
import importlib.resources as pkg_resources

def setup_pycavi(destination="."):
    """Copy all notebooks from pycavi/notebooks to the working directory."""

    try:
        config_package = "pycavi.config"
        config_path = pkg_resources.files(config_package)

        # Check if the path is valid
        if not config_path.is_dir():
            print("No config directory found in the installed package.")
            return

        os.makedirs(destination+"/config", exist_ok=True)

        for cfgfile in config_path.iterdir():
            if cfgfile.suffix == ".cfg" or cfgfile.suffix == ".paf":
                shutil.copy(cfgfile, os.path.join(destination+"/config", cfgfile.name))
                print(f"Copied: {cfgfile.name} -> {destination+'/config'}")

    except Exception as e:
        print(f"Error copying configuration files while setting up PyCavi: {e}")

    try:
        notebooks_package = "pycavi.notebooks"
        notebooks_path = pkg_resources.files(notebooks_package)

        # Check if the path is valid
        if not notebooks_path.is_dir():
            print("No notebooks directory found in the installed package.")
            return

        os.makedirs(destination, exist_ok=True)

        for notebook in notebooks_path.iterdir():
            if notebook.suffix == ".ipynb":
                shutil.copy(notebook, os.path.join(destination, notebook.name))
                print(f"Copied: {notebook.name} -> {destination}")

    except Exception as e:
        print(f"Error copying notebooks while setting up PyCavi: {e}")

if __name__ == "__main__":
    setup_pycavi()

