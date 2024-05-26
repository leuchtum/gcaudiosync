import numpy as np
import copy
import math
import gcaudiosync.gcanalyser.vectorfunctions as vecfunc

class Movement:

    expected_time: int = 0          # Expected time for this movement

    start_vector_linear_axes    = np.array([0.0, 0.0, 0.0])         # Start vector for the linear axes
    end_vector_linear_axes      = np.array([0.0, 0.0, 0.0])         # End vector for the linear axes

    start_vector_rotation_axes  = np.array([0.0, 0.0, 0.0])         # Start vector for the rotation axes
    end_vector_rotation_axes    = np.array([0.0, 0.0, 0.0])         # End vector for the rotation axes

    # Constructor
    def __init__(self,
                 line_index: int,
                 movement: int = -1,
                 start_position_linear_axes = np.array([0.0, 0.0, 0.0]), 
                 end_position_linear_axes = np.array([0.0, 0.0, 0.0]),
                 start_position_rotation_axes = np.array([0.0, 0.0, 0.0]),
                 end_position_rotation_axes = np.array([0.0, 0.0, 0.0]),
                 info_arc = None,
                 feed_rate: float = 0.0):
        
        self.line_index = line_index                                # Set line index

        self.movement = movement                                    # Set movement

        self.start_position_linear_axes = start_position_linear_axes        # Set start position for linear axes
        self.end_position_linear_axes  = end_position_linear_axes           # Set end position for linear axes

        self.start_position_rotation_axes  = start_position_rotation_axes   # Set start position for rotation axes
        self.end_position_rotation_axes = end_position_rotation_axes        # Set end position for rotation axes

        self.info_arc = copy.deepcopy(info_arc)                     # all infos for an arc: 
                                                                    # [direction, I, J, K, R, #turns]
                                                                    # direction: 2 -> CW, 3 -> CCW
                                                                    # I, J, K: absolute arc center in mm
                                                                    # R: radius in mm
                                                                    # #turns: number of turns

        self.feed_rate = feed_rate                          # Set feed rate

        # Check if movement is valid: compute optimal vectors and expected time
        if movement != -1:
            self.compute_optimal_start_vector_linear_axes() 
            self.compute_optimal_start_vector_rotation()
            self.compute_optimal_end_vector_linear_axes()
            self.compute_optimal_end_vector_rotation()
            self.compute_expected_time()

    #################################################################################################
    # Methods

    # Method to compute optimal start vector for linear axes # TODO: comment
    def compute_optimal_start_vector_linear_axes(self):
        
        if self.movement in [0, 1]:
            start_vector_linear = self.end_position_linear_axes - self.start_position_linear_axes
            vector_length = np.linalg.norm(start_vector_linear)
            if vector_length > 0:
                self.start_vector_linear_axes = start_vector_linear / vector_length * self.feed_rate
            else:
                pass
        else:
            XY_normal_vector = np.array([0.0, 0.0, 1.0])
            arc_center = self.info_arc[1:4]
            arc_center_2_start = self.start_position_linear_axes - arc_center
            
            if self.movement == 2:
                self.start_vector_linear_axes = vecfunc.compute_normal_vector(arc_center_2_start, XY_normal_vector, "right") * self.feed_rate
            else: 
                self.start_vector_linear_axes = vecfunc.compute_normal_vector(arc_center_2_start, XY_normal_vector, "left") * self.feed_rate

    # TODO
    def compute_optimal_start_vector_rotation(self):
        pass

    # Method to compute optimal end vector for linear axes # TODO: comment    
    def compute_optimal_end_vector_linear_axes(self):
        
        if self.movement in [0, 1]:
            end_vector_linear = self.end_position_linear_axes - self.start_position_linear_axes
            vector_length = np.linalg.norm(end_vector_linear)
            if vector_length > 0:
                self.end_vector_linear_axes = end_vector_linear / vector_length * self.feed_rate
            else:
                pass
        else:
            XY_normal_vector = np.array([0.0, 0.0, 1.0])
            arc_center = self.info_arc[1:4]
            arc_center_2_end = self.end_position_linear_axes - arc_center
            
            if self.movement == 2:
                self.end_vector_linear_axes = vecfunc.compute_normal_vector(arc_center_2_end, XY_normal_vector, "right") * self.feed_rate
            else: 
                self.end_vector_linear_axes = vecfunc.compute_normal_vector(arc_center_2_end, XY_normal_vector, "left") * self.feed_rate

    # TODO
    def compute_optimal_end_vector_rotation(self):
        pass

    # Method to set vectors to exact stop # TODO: comment
    def do_exact_stop(self):
        self.end_vector_linear_axes = np.array([0.0, 0.0, 0.0])
        self.end_vector_rotation_axes = np.array([0.0, 0.0, 0.0])

    # Method to compute the expected time # TODO: comment
    def compute_expected_time(self):

        if self.movement == -1:
            return
        
        # start_velocity_linear = np.linalg.norm(self.start_vector_linear)
        # end_velocity_linear = np.linalg.norm(self.end_Vector_linear)

        target_velocity = self.feed_rate

        if target_velocity == 0:
            raise Exception(f"F value is 0 in line {self.line_index+1}.")
        
        if self.movement in [0, 1]:
            distance = np.linalg.norm(self.end_position_linear_axes - self.start_position_linear_axes)
        
        else:

            start_position_linear_axes = copy.deepcopy(self.start_position_linear_axes)
            end_position_linear_axes = copy.deepcopy(self.end_position_linear_axes)
            arc_center = copy.deepcopy(self.info_arc[1:4])

            distance_Z = end_position_linear_axes[2] - start_position_linear_axes[2]

            start_position_linear_axes[2] = 0
            end_position_linear_axes[2] = 0
            arc_center [2] = 0

            center_2_start = start_position_linear_axes - arc_center
            center_2_end = end_position_linear_axes - arc_center

            radius = abs(self.info_arc[4])
            turns: float = float(self.info_arc[5])

            if self.info_arc[4] >= 0:
                smaller_angle = True
            else:
                smaller_angle = False

            angle: float = vecfunc.compute_angle(center_2_start, center_2_end, smaller_angle)
            
            circumference: float = 2.0*math.pi*radius

            arc_distance: float = (turns + angle / 360.0) * circumference
            
            distance = math.sqrt(math.pow(arc_distance, 2) + math.pow(distance_Z, 2))

        self.expected_time = int(distance / target_velocity)

    # Method to get the position of linear axes in a movement at a given time # TODO: comment
    def get_position_linear_axes_in_movement(self, 
                                             time_in_movement: int):

        position = np.array([0.0, 0.0, 0.0])

        if self.movement == -1:
            position = copy.deepcopy(self.start_position_linear_axes)
        elif self.movement in [0, 1]:
            position = self.start_position_linear_axes + self.start_vector_linear_axes * time_in_movement
        else:
            start_point_linear = copy.deepcopy(self.start_position_linear_axes)
            end_point_linear = copy.deepcopy(self.end_position_linear_axes)
            arc_center = copy.deepcopy(self.info_arc[1:4])

            center_2_start = start_point_linear - arc_center
            center_2_end = end_point_linear - arc_center

            start_point_linear[2] = 0
            end_point_linear[2] = 0
            arc_center[2] = 0

            radius = abs(self.info_arc[4])
            turns = self.info_arc[5]

            if self.info_arc[4] >= 0:
                smaller_angle = True
            else:
                smaller_angle = False

            angle = vecfunc.compute_angle(center_2_start, center_2_end, smaller_angle)

            total_angle = angle + 360.0 * turns

            portion = time_in_movement / self.expected_time

            current_angle = portion * total_angle

            if self.movement == 2:
                current_angle *= -1

            center_2_start = center_2_start[0:2]
            arc_center = arc_center[0:2]
            XY_position = vecfunc.rotate_2D_vector(center_2_start, arc_center, current_angle)
            
            position[0] = XY_position[0]
            position[1] = XY_position[1]

            distance_Z = self.end_position_linear_axes[2] - self.start_position_linear_axes[2]
            current_Z = self.start_position_linear_axes[2] + portion * distance_Z
            position[2] = current_Z

        return np.round(position, 3)

    # Method to print info of movement # TODO: comment
    def print_info(self):
        print(f"Movement in line {self.line_index+1}")
        print(f"Movement: {self.movement}")
        print(f"Start point: {self.start_position_linear_axes}")
        print(f"End point: {self.end_position_linear_axes}")
        print(f"Start vector: {self.start_vector_linear_axes}")
        print(f"End vector: {self.end_vector_linear_axes}")

        if self.movement in [2, 3]:
            print(f"Arc info: {self.info_arc}")
        
        print(f"feed rate [mm/ms]: {self.feed_rate}")
        print(f"Expected time: {self.expected_time}")

# End of class
#####################################################################################################
