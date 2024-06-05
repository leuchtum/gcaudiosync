import numpy as np
import copy

class RotationAxes:


    # Constructor
    def __init__(self,
                 A: float = 0.0,
                 B: float = 0.0,
                 C: float = 0.0):
        
        self.A = A
        self.B = B
        self.C = C

    #################################################################################################
    # Methods

    def set_with_array(self, 
                       new_coordinates_as_array):
        """
        Set the rotation angles using an array.

        Args:
            new_coordinates (np.ndarray): An array containing the A, B, and C rotation angles.
        """

        self.A = float(copy.copy(new_coordinates_as_array[0]))
        self.B = float(copy.copy(new_coordinates_as_array[1]))
        self.C = float(copy.copy(new_coordinates_as_array[2]))

    def get_as_array(self) -> np.ndarray:
        """
        Get the rotation angles as a numpy array.

        Returns:
            np.ndarray: An array containing the A, B, and C rotation angles.
        """

        array = np.array([self.A, self.B, self.C])
        return copy(array)
    
    def print(self):
        """
        Print the rotation angles.

        This method prints the rotation angles around the A, B, and C axes.
        """

        print(f"X = {self.X}, Y = {self.Y}, Z = {self.Z}")

# End of class
#####################################################################################################