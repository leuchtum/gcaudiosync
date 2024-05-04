import numpy as np
import math

def compute_normal_vector(vec1, 
                          vec2, 
                          direction):  
    normal_vector = np.cross(vec1, vec2)

    length_normal_vector = np.linalg.norm(normal_vector)

    if length_normal_vector == 0:
        raise Exception("Cannot compute normal vector with two identical vactors.")
    
    if direction == "left":
        normal_vector = normal_vector * -1

    normal_vector = normal_vector / length_normal_vector

    return normal_vector

def equal(vec1, vec2):
    
    if len(vec1) != len(vec2):
        raise Exception("Vectors must have the same length")

    for index in range(len(vec1)):

        if vec1[index] != vec2[index]:
            return False

        return True

def same_direction(vec1, vec2):

    if len(vec1) != len(vec2):
        raise Exception("Vectors must have the same length")
    
    factor_found = False
    factor = 0

    for index in range(len(vec1)):
        if not(vec1[index] != 0 and vec2[index] != 0):
            if not vec1[index] == vec2[index]:
                return False
        else:
            new_factor = vec1[index] / vec2[index]
            if factor_found and factor != new_factor:
                return False
            elif not factor_found:
                factor = new_factor
    return True

def get_factor(vec1, vec2):

    if len(vec1) != len(vec2):
        raise Exception("Vectors must have the same length")
    
    if not same_direction(vec1, vec2):
        raise Exception("Vectors are not pointing in the same direction")
    
    factor = 0
    factor_found = False

    for index in range(len(vec1)):
        if vec1[index] != 0:
            factor = vec1[index] / vec2[index]
            break
    
    return factor

def compute_angle(vec1: np.ndarray, vec2: np.ndarray, smaller_angle: np.bool_) -> float:
    """
    Calculates the smaller or bigger angle between two NumPy arrays in degrees.

    Args:
        vec1 (np.ndarray):              First NumPy array.
        vec2 (np.ndarray):              Second NumPy array.
        smaller_angle (bool, optional): Whether to return the smaller angle (True, default) or the bigger angle (False).

    Returns:
        float: The requested angle (smaller or bigger) between the two vectors in degrees.

    Raises:
        ValueError: If the input vectors are not valid NumPy arrays or have zero norm.
    """

    # Handle potential division by zero
    if np.linalg.norm(vec1) == 0 or np.linalg.norm(vec2) == 0:
        raise ValueError("Cannot calculate angle for zero-norm vectors.")

    # Calculate cosine of the angle
    cosine = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    # Ensure cosine value is within valid range (-1, 1)
    cosine = np.clip(cosine, -1, 1)

    # Calculate the angle in degrees
    angle_degrees = np.degrees(np.arccos(cosine))

    # Return requested angle
    return min(angle_degrees, 360 - angle_degrees) if smaller_angle else max(angle_degrees, 360 - angle_degrees)

def rotate_2D_vector(center_2_point, center, angle):

    rotation_matrix = np.array([[math.cos(math.radians(angle)), -math.sin(math.radians(angle))], 
                                [math.sin(math.radians(angle)), math.cos(math.radians(angle))]])

    new_vec = rotation_matrix @ center_2_point + center

    return new_vec

def get_best_start_vector(vec_end, vec_start_next):
    pass
