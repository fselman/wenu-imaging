import os
import re
import pkg_resources
import toml

# Directories to scan for dependencies
SCAN_DIRS = ["papi", "pycavi", "scripts"]

# Packages to ignore (standard libraries and built-ins)
IGNORED_PACKAGES = {"os", "sys", "re", "json", "time", "datetime", "math", "random"}

def extract_imports_from_file(file_path):
    """Extracts imported libraries from a Python file."""
    imports = set()
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            match = re.match(r"^\s*(?:import|from) (\w+)", line)
            if match:
                package = match.group(1).split(".")[0]  # Get top-level package
                if package not in IGNORED_PACKAGES:
                    imports.add(package)
    return imports

def find_dependencies():
    """Scans directories to find imported dependencies."""
    dependencies = set()
    for directory in SCAN_DIRS:
        if os.path.exists(directory):
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.endswith(".py"):
                        file_path = os.path.join(root, file)
                        dependencies.update(extract_imports_from_file(file_path))
    return dependencies

def get_installed_versions(dependencies):
    """Gets installed versions of dependencies."""
    installed_packages = {pkg.key: pkg.version for pkg in pkg_resources.working_set}
    return {dep: installed_packages.get(dep, "*") for dep in dependencies}

def generate_pyproject(dependencies):
    """Creates a pyproject.toml file."""
    pyproject_data = {
        "build-system": {
            "requires": ["setuptools", "wheel"],
            "build-backend": "setuptools.build_meta",
        },
        "project": {
            "name": "your-module-name",
            "version": "0.1.0",
            "description": "Your Python module description",
            "authors": [{"name": "Your Name", "email": "your.email@example.com"}],
            "license": {"file": "LICENSE"},
            "dependencies": [f"{pkg}=={version}" for pkg, version in dependencies.items()],
        },
        "tool": {
            "setuptools": {
                "packages": ["papi", "pycavi"],
                "package-data": {
                    "config": ["*.txt", "*.json", "*.paf", "*.cfg"],
                    "data": ["*.csv", "*.json"]
                }
            }
        },
        "project.scripts": {
            "notebook_0i": "scripts.0i_script:main",
        }
    }

    # Save to pyproject.toml
    with open("pyproject.toml", "w", encoding="utf-8") as f:
        toml.dump(pyproject_data, f)

    print("✅ pyproject.toml generated successfully!")

# Run the process
dependencies = find_dependencies()
dependencies_with_versions = get_installed_versions(dependencies)
generate_pyproject(dependencies_with_versions)
