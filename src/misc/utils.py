import os
import json
from pathlib import Path
from ursina import Texture, Color
    
def _serialize_data(data):
    """Convert non-serializable objects to JSON-compatible types."""
    if isinstance(data, dict):
        return {key: _serialize_data(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [_serialize_data(item) for item in data]
    elif isinstance(data, Texture):
        return str(data.path)
    elif isinstance(data, Color):
        return str(data)
    elif hasattr(data, "__dict__"):
            return _serialize_data(data.__dict__)
    else:
        return data
    
def _is_texture(data):
    """
    Checks if the string represents a valid Texture.
    You can customize this function based on your requirements.
    """
    valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff')
    return isinstance(data, str) and data.lower().endswith(valid_extensions)

def _is_color(data):
    """
    Check if the string represents a valid Color object.
    """
    if isinstance(data, str) and data.startswith('Color(') and data.endswith(')'):
        try:
            # Extract the values inside 'Color(...)'
            color_values = data[6:-1].split(', ')
            # Ensure they are valid float numbers
            return len(color_values) == 4 and all(0 <= float(v) <= 1 for v in color_values)
        except ValueError:
            return False
    return False
    
def _deserialize_data(data):
    """Convert JSON-compatible types back to their original objects."""
    if isinstance(data, dict):
        return {key: _deserialize_data(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [_deserialize_data(item) for item in data]
    elif isinstance(data, str):
        if _is_texture(data):
            return Texture(data)
        elif _is_color(data):
            color_values = data[6:-1].split(', ')
            r, g, b, a = map(float, color_values) 
            return Color(r, g, b, a)
        else:
            return data
    else:
        return data
    
def json_save(data, filename: str):
    file_path = Path(filename)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    serializable_data = _serialize_data(data)
    with open(file_path, "w") as file:
        json.dump(serializable_data, file, indent=4)
    print(f"{file_path} saved successfully!")

def json_load(file_path: str):
    """
    Read a JSON file from a specified file_path and deserialize its contents.
    """
    with open(file_path) as f:
        data = json.load(f)
    return _deserialize_data(data)

def get_files_in_folder(folder_path: str):
    """
    Returns a list of tuples containing file names (without extensions) and their full paths.
    
    Args:
        folder_path (str): Path to the folder.
    
    Returns:
        list: A list of tuples [(file_name, full_path), ...].
    """
    file_list = []

    # Iterate through all files in the folder
    for file in os.listdir(folder_path):
        full_path = os.path.join(folder_path, file)
        # Check if it's a file
        if os.path.isfile(full_path):
            file_name, _ = os.path.splitext(file)  # Get the name without the extension
            file_list.append((file_name, full_path))
    
    return file_list