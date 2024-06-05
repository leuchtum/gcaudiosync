import numpy as np

class ToolPathInformation:

    g_code_line_index: int = 0
    position_linear_axes = np.zeros(3)
    movement_type: int = 0

    def __init__(self):
        pass