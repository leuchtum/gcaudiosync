import numpy as np

from gcaudiosync.gcanalyser.linearaxes import LinearAxes

class ToolPathInformation:
    """
    Contains information about the toolpath

    Attributes:
    ----------
        g_code_line_index : int
            indec of the g-code-line
        position_linear_axes : np.array
            X, Y and Z coordinates of the position
        movement_type : int
            movement-type: 
            0: rapid linear movement
            1: linear movement
            2: arc CW
            3: arc CCW
    """
    def __init__(self):
        """
        Initializes the ToolPathInformation object
        """
        self.g_code_line_index: int = 0
        self.position_linear_axes: np.array = np.zeros(3)
        self.movement_type: int = 0