import numpy as np

class Movement:

    time = 0

    start_vector_linear = np.array([0.0, 0.0, 0.0])
    end_vector_linear = np.array([0.0, 0.0, 0.0])

    start_vector_rotation = np.array([0.0, 0.0, 0.0])
    end_vector_rotation = np.array([0.0, 0.0, 0.0])

    def __init__(self,
                 line_index: int,
                 movement = 0,
                 start_point_linear = np.array([0.0, 0.0, 0.0]), 
                 end_point_linear = np.array([0.0, 0.0, 0.0]),
                 start_point_rotation = np.array([0.0, 0.0, 0.0]),
                 end_point_rotation = np.array([0.0, 0.0, 0.0]),
                 info_arc = None):
        
        self.line_index = line_index

        self.movement = movement

        self.start_point_linear = start_point_linear
        self.end_point_linear = end_point_linear

        self.start_point_rotation = start_point_rotation
        self.end_point_rotation = end_point_rotation

        self.info_arc = info_arc         # [direction, I, J, K, R, #turns]

        self.compute_optimal_start_vector()
        self.compute_optimal_end_vector()
        
    def compute_optimal_start_vector(self):
        pass

    def compute_optimal_end_vector(self):
        pass