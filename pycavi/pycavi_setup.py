import os
import shutil
import importlib.resources as pkg_resources

def setup_pycavi(destination="."):
    """Copy all notebooks from pycavi/notebooks to the working directory."""
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
        print(f"Error setting up PyCavi: {e}")

if __name__ == "__main__":
    setup_pycavi()

