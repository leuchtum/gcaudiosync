import numpy as np
import copy

class RotationAxes:

    def __init__(self,
                 A: float = 0.0,
                 B: float = 0.0,
                 C: float = 0.0):
        
        self.A = A
        self.B = B
        self.C = C

    def set_with_array(self, new_coordinates):
        self.A = copy(new_coordinates[0])
        self.B = copy(new_coordinates[1])
        self.C = copy(new_coordinates[2])

    def get_as_array(self):
        array = np.array([self.A, self.B, self.C])
        return copy(array)
    
    def print(self):
        print(f"X = {self.X}, Y = {self.Y}, Z = {self.Z}")
