import numpy as np
import copy

class RotationAxes:
    """
    Represents the rotationsl axes in a CNC machine.

    This class stores the A, B, and C coordinates of the axes in degrees.

    Attributes:
        A (float): The A-value.
        B (float): The B-value.
        C (float): The C-value.
    """

    # Constructor
    def __init__(self,
                 A: float = 0.0,
                 B: float = 0.0,
                 C: float = 0.0):
        """
        Initializes the RotationAxes object.

        Args:
            A (float, optional): The A-value. Defaults to 0.0.
            B (float, optional): The B-value. Defaults to 0.0.
            C (float, optional): The C-value. Defaults to 0.0.
        """
        
        self.A: float = A
        self.B: float = B
        self.C: float = C

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
        return copy.copy(array)
    
    def print(self):
        """
        Print the rotation angles.

        This method prints the rotation angles around the A, B, and C axes.
        """

        print(f"X = {self.X}, Y = {self.Y}, Z = {self.Z}")

# End of class
#####################################################################################################