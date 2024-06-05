import numpy as np
import copy

class ArcInformation:
    """
    Represents information about an arc in CNC machining.

    This class stores information about an arc, including its direction,
    arc center coordinates, and radius.

    Attributes:
        direction (int): The direction of the arc (2 for clockwise, 3 for counterclockwise).
        I (float): The absolute X-coordinate of the arc center.
        J (float): The absolute Y-coordinate of the arc center.
        K (float): The absolute Z-coordinate of the arc center.
        radius (float): The radius of the arc.
    """

    # Constructor
    def __init__(self,
                 direction: int = 2,
                 I: float = 0.0,
                 J: float = 0.0,
                 K: float = 0.0,
                 radius = 0):
        """
        Initializes the ArcInformation object.

        Args:
            direction (int, optional): The direction of the arc (2 for clockwise, 3 for counterclockwise). Defaults to 2.
            I (float, optional): The X-coordinate of the arc center. Defaults to 0.0.
            J (float, optional): The Y-coordinate of the arc center. Defaults to 0.0.
            K (float, optional): The Z-coordinate of the arc center. Defaults to 0.0.
            radius (float, optional): The radius of the arc. Defaults to 0.
        """

        self.direction = direction
        self.I = I
        self.J = J
        self.K = K
        self.radius = radius
    
    #################################################################################################
    # Methods

    def get_arc_center_as_array(self):
        """
        Get the coordinates of the arc center as a numpy array.

        Returns:
            np.ndarray: An array containing the X, Y, and Z coordinates of the arc center.
        """
        arc_center_as_array = np.array([self.I, self.J, self.K])
        return copy.copy(arc_center_as_array)
    
    def set_arc_center(self, arc_center_as_array):
        """
        Set the coordinates of the arc center.

        Args:
            arc_center (np.ndarray): An array containing the X, Y, and Z coordinates of the arc center.
        """
        self.I = arc_center_as_array[0]
        self.J = arc_center_as_array[1]
        self.K = arc_center_as_array[2]
    
    def print(self):
        """
        Print information about the arc.

        This method prints the direction, arc center coordinates, and radius of the arc.
        """
        print(f"direction: {self.direction}; arc-center (absolut): I = {self.I}, J = {self.J}, K = {self.K}; radius: {self.radius}")

# End of class
#####################################################################################################
