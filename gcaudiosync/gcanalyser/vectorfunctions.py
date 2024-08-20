import numpy as np
import copy
import math

def compute_normal_vector(vec1, 
                          vec2, 
                          direction):  
    """
    Computes the normal vector to two given vectors.

    Parameters:
    -----------
        vec1: first vector
        vec2: second vector
        direction: left or right
    
    Returns:
    -------
        normal vector
    """
    normal_vector = np.cross(vec1, vec2)

    length_normal_vector = np.linalg.norm(normal_vector)

    if length_normal_vector == 0:
        raise Exception("Cannot compute normal vector with two identical vactors.")
    
    if direction == "left":
        normal_vector = normal_vector * -1

    normal_vector = normal_vector / length_normal_vector

    return normal_vector

def equal(vec1, vec2):
    """
    Checks if two vectors are equal.

    Parameters:
    ----------
        vec1: first vector
        vec2: second vector

    Returns:
    --------
        bool
    """
    if len(vec1) != len(vec2):
        raise Exception("Vectors must have the same length")

    for index in range(len(vec1)):

        if vec1[index] != vec2[index]:
            return False

        return True

def same_direction(vec1, vec2):
    """
    Checks if two vectors point into the same direction.

    Parameters:
    ----------
        vec1: first vector
        vec2: second vector
    
    Returns:
    --------
        bool
    """

    if len(vec1) != len(vec2):
        raise Exception("Vectors must have the same length")
    
    if np.dot(normalize(vec1), normalize(vec2)) > 0.999:
        return True
    else:
        return False
    
def opposite_direction(vec1, vec2):
    """
    Checks if two vectors point into the oppisite direction.

    Parameters:
    ----------
        vec1: first vector
        vec2: second vector

    Returns:
    --------
        bool
    """

    if len(vec1) != len(vec2):
        raise Exception("Vectors must have the same length")
    
    if np.dot(normalize(vec1), normalize(vec2)) < -0.999:
        return True
    else:
        return False

def get_factor(vec1, vec2):
    """
    Computes the factor between two vectors that point into the same direction. factor = vec1 / vec2.

    Parameters:
    ----------
        vec1: first vector
        vec2: second vector

    Returns:
    -------
        factor between the two vectors
    """

    if len(vec1) != len(vec2):
        raise Exception("Vectors must have the same length")
    
    if not same_direction(vec1, vec2) and not opposite_direction(vec1, vec2):
        raise Exception("Vectors are not pointing in the same or opposite direction")
    
    factor = 0

    for index in range(len(vec1)):
        if vec2[index] != 0:
            factor = vec1[index] / vec2[index]
            break
    
    return factor

def compute_smaller_angle_in_degree(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Computes the smaller angle between two vectors.

    Parameters:
    ----------
        vec1: first vector
        vec2: second vector
    Returns:
    --------
        smaller angle between the two vectors.
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

    return angle_degrees

def compute_small_or_big_angle_in_degree(vec1: np.ndarray, vec2: np.ndarray, smaller_angle: np.bool_) -> float:
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

    smaller_angle_degrees = compute_smaller_angle_in_degree(vec1 = vec1, vec2 = vec2)

    # Return requested angle
    return smaller_angle_degrees if smaller_angle else 360 - smaller_angle_degrees

def compute_small_or_big_angle(vec1: np.ndarray, vec2: np.ndarray, smaller_angle: np.bool_) -> float:
    """
    Calculates the smaller or bigger angle between two NumPy arrays in rad.

    Args:
        vec1 (np.ndarray):              First NumPy array.
        vec2 (np.ndarray):              Second NumPy array.
        smaller_angle (bool, optional): Whether to return the smaller angle (True, default) or the bigger angle (False).

    Returns:
        float: The requested angle (smaller or bigger) between the two vectors in rad.

    Raises:
        ValueError: If the input vectors are not valid NumPy arrays or have zero norm.
    """
    # Compute angele
    smaller_angle_in_degree = compute_smaller_angle_in_degree(vec1, vec2)
    smaller_angle_in_rad = smaller_angle_in_degree / 360.0 * 2 * math.pi

    # Return requested angle
    return smaller_angle_in_rad if smaller_angle else 360 - smaller_angle_in_rad

def compute_angle_from_X_axis(vec: np.array) -> float:
    """
    Calculates the angle between a vector and the X-axis

    Args:
        vec1 (np.ndarray): NumPy array.

    Returns:
        float: The requested angle
    """

    if len(vec) != 2:
        raise Exception(f"Vector must be 2D")
    
    smaller_angle_degree = compute_smaller_angle_in_degree(vec1 = np.array([1, 0]), vec2 = copy.copy(vec))

    if vec[1] >= 0:
        return smaller_angle_degree
    else:
        return 360 - smaller_angle_degree

def rotate_2D_vector(center_2_point, center, angle):
    """
    Rotatats a 2D-vector about a given angele

    Args:
        center_2_point: vector
        center: start of the vector
        angle: angle

    Returns:
        Rotated vector
    """

    rotation_matrix = np.array([[math.cos(math.radians(angle)), -math.sin(math.radians(angle))], 
                                [math.sin(math.radians(angle)), math.cos(math.radians(angle))]])

    new_vec = rotation_matrix @ center_2_point + center

    return new_vec

def normalize(vec_in):
    """
    Normalizes a vector

    Args:
        vec_in: vector

    Returns:
        normalized vector
    """
    vec = copy.copy(vec_in)

    if np.linalg.norm(vec) == 0:
        return vec
    
    vec = vec / np.linalg.norm(vec)
    return vec