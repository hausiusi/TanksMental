import os
import json
import math
from pathlib import Path
from ursina import Texture, Color, Vec3, raycast, Entity

    
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

def normalize(v):
    """Returns the normalized Vec3."""
    return v.normalized()

def rotate_vector(vec, axis, angle):
    """
    Rotates a vector around a given axis by a specified angle using Rodrigues' rotation formula.
    
    Parameters:
    - vec: Vec3, the vector to rotate.
    - axis: Vec3, the axis to rotate around.
    - angle: float, rotation angle in radians.

    Returns:
    - Vec3, the rotated vector.
    """
    axis = normalize(axis)
    cos_theta = math.cos(angle)
    sin_theta = math.sin(angle)
    
    return (vec * cos_theta +
            axis.cross(vec) * sin_theta +
            axis * axis.dot(vec) * (1 - cos_theta))

def rotate_vector_around_y(vec, angle):
    """
    Rotates a vector around the Z-axis by a specified angle.
    
    Parameters:
    - vec: Vec3, the vector to rotate.
    - angle: float, rotation angle in radians.

    Returns:
    - Vec3, the rotated vector.
    """
    cos_theta = math.cos(angle)
    sin_theta = math.sin(angle)

    return Vec3(
        vec.x * cos_theta - vec.y * sin_theta,  # X rotation
        vec.x * sin_theta + vec.y * cos_theta,   # Y rotation
        vec.z  # Y stays the same
    )

def raycast_around(vec, theta, n_rays, entity:Entity, distance=2, ignore=[], debug=False):
    """
    This function is for debugging. It's heavy and affects the framerate dramatically.
    The better variant is to use frame-by-frame scanning around, that means one raycast per frame
    with different angles.

    Parameters:
    - vec: Vec3, the direction vector of the entity
    - theta: angle that will be raycasted from left to right. e.g. if it's 0.2rad means that 0.2 radians
        will be raycasted on the left and 0.2 radians on the right
    - entity: the entity that emits the raycasts
    - distance: length of raycast
    - ignore[]: the entities that must be ignored while collecting the ray-hits
    - debug: if true the rays will be visible and the hit entities will be printed in console
    """
    theta_step = theta / n_rays
    theta_current = 0
    for i in range(n_rays):
        theta_current += theta_step        
        slightly_left = rotate_vector_around_y(vec, theta_current)
        slightly_right = rotate_vector_around_y(vec, -theta_current)
        ray_left = raycast(entity.position, slightly_left, ignore=ignore, distance=distance, debug=debug)
        ray_right = raycast(entity.position, slightly_right, ignore=ignore, distance=distance, debug=debug)

        # TODO: collect all entities and return them
        if debug:
            if ray_left.hit:
                print(ray_left.entities)
            if ray_right.hit:
                print(ray_right.entities)
