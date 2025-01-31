# FileName: map_list_logic.py
# version: 1.1
# Summary: Provides logic for listing, deleting, and checking map files (JSON)
#          in the "maps" directory, separate from any specific rendering or UI.
# Tags: map, logic, files

import os

def ensure_maps_dir_exists(maps_dir="maps"):
    """
    Ensures that the maps_dir folder exists, creating it if needed.
    """
    os.makedirs(maps_dir, exist_ok=True)

def get_map_list(maps_dir="maps", extension=".json"):
    """
    Return a sorted list of all files in 'maps_dir' ending with 'extension'.
    Ensures that 'maps_dir' is created if missing.
    """
    ensure_maps_dir_exists(maps_dir)
    files = [f for f in os.listdir(maps_dir) if f.endswith(extension)]
    files.sort()
    return files

def delete_map_file(filename, maps_dir="maps"):
    """
    Attempt to delete 'filename' inside 'maps_dir'.
    Return True on successful deletion, False on failure.
    """
    file_path = os.path.join(maps_dir, filename)
    try:
        os.remove(file_path)
        return True
    except OSError:
        return False

def file_exists_in_maps_dir(filename, maps_dir="maps"):
    """
    Return True if 'filename' exists inside 'maps_dir'.
    """
    file_path = os.path.join(maps_dir, filename)
    return os.path.isfile(file_path)