import numpy as np

from gcaudiosync.gcanalyser.linearaxes import LinearAxes

class ToolPathInformation:

    g_code_line_index: int = 0
    position_linear_axes: np.array = np.zeros(3)
    movement_type: int = 0

    def __init__(self):
        pass