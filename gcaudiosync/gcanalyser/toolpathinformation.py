import numpy as np

class ToolPathInformation:

    line_index: int = 0
    position_linear_axes = np.zeros(3)
    movement: int = 0

    def __init__(self):
        pass