import numpy as np
import copy

class LinearAxes:

    def __init__(self,
                 X: float = 0.0,
                 Y: float = 0.0,
                 Z: float = 0.0):
        
        self.X = X
        self.Y = Y
        self.Z = Z
        
    def set_with_array(self, 
                       new_coordinates):
        self.X = copy(new_coordinates[0])
        self.Y = copy(new_coordinates[1])
        self.Z = copy(new_coordinates[2])

    def get_as_array(self):
        array = np.array([self.X, self.Y, self.Z])
        return copy.copy(array)
    
    def print(self):
        print(f"X = {self.X}, Y = {self.Y}, Z = {self.Z}")
