import numpy as np

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

