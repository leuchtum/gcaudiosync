import numpy as np
import copy

class LinearAxes:
    """
    Represents the linear axes in a CNC machine.

    This class stores the X, Y, and Z coordinates of a point in a Cartesian coordinate system.

    Attributes:
        X (float): The X-coordinate.
        Y (float): The Y-coordinate.
        Z (float): The Z-coordinate.
    """

    # Constructor
    def __init__(self,
                 X: float = 0.0,
                 Y: float = 0.0,
                 Z: float = 0.0):
        """
        Initializes the LinearAxes object.

        Args:
            X (float, optional): The X-coordinate. Defaults to 0.0.
            Y (float, optional): The Y-coordinate. Defaults to 0.0.
            Z (float, optional): The Z-coordinate. Defaults to 0.0.
        """

        self.X = X
        self.Y = Y
        self.Z = Z

    #################################################################################################
    # Methods

    def set_with_array(self, 
                       new_coordinates_as_array):
        """
        Set the coordinates using an array.

        Args:
            new_coordinates (np.ndarray): An array containing the X, Y, and Z coordinates.
        """
        self.X = copy(new_coordinates_as_array[0])
        self.Y = copy(new_coordinates_as_array[1])
        self.Z = copy(new_coordinates_as_array[2])

    def get_as_array(self):
        """
        Get the coordinates as a numpy array.

        Returns:
            np.ndarray: An array containing the X, Y, and Z coordinates.
        """
        array = np.array([self.X, self.Y, self.Z])
        return copy.copy(array)
    
    def print(self):
        """
        Print the coordinates.

        This method prints the X, Y, and Z coordinates.
        """
        print(f"X = {self.X}, Y = {self.Y}, Z = {self.Z}")

# End of class
#####################################################################################################
