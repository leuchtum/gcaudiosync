import numpy as np
import copy
import math

import gcaudiosync.gcanalyser.vectorfunctions as vecfunc

from gcaudiosync.gcanalyser.linearaxes import LinearAxes
from gcaudiosync.gcanalyser.rotationaxes import RotationAxes
from gcaudiosync.gcanalyser.arcinformation import ArcInformation

class Movement:

    start_time: int = 0             # Time when the movement starts
    time: int = 0                   # Time for this movement

    start_vector_linear_axes    = np.array([0.0, 0.0, 0.0])         # Start vector for the linear axes
    end_vector_linear_axes      = np.array([0.0, 0.0, 0.0])         # End vector for the linear axes

    start_vector_rotation_axes  = np.array([0.0, 0.0, 0.0])         # Start vector for the rotation axes
    end_vector_rotation_axes    = np.array([0.0, 0.0, 0.0])         # End vector for the rotation axes

    start_time_is_adjustable: bool = True       # shows if the start time of this movement is adjustable
    time_is_adjustable: bool = True             # shows if the time of this movement is adjustable

    # Constructor
    def __init__(self,
                 line_index: int,
                 movement_type: int,
                 start_position_linear_axes: LinearAxes, 
                 end_position_linear_axes: LinearAxes,
                 start_position_rotation_axes: RotationAxes,
                 end_position_rotation_axes: RotationAxes,
                 arc_information: ArcInformation,
                 feed_rate: float):
        
        # save all parameters
        self.line_index                     = line_index
        self.movement_type                  = movement_type
        self.start_position_linear_axes     = copy.deepcopy(start_position_linear_axes)
        self.end_position_linear_axes       = copy.deepcopy(end_position_linear_axes)
        self.start_position_rotation_axes   = copy.deepcopy(start_position_rotation_axes)
        self.end_position_rotation_axes     = copy.deepcopy(end_position_rotation_axes)
        self.arc_information                = copy.deepcopy(arc_information)
        self.feed_rate                      = feed_rate

        # Check if movement is valid: compute optimal vectors and expected time
        if movement_type != -1:
            self.compute_optimal_start_vector_linear_axes() 
            self.compute_optimal_start_vector_rotation()
            self.compute_optimal_end_vector_linear_axes()
            self.compute_optimal_end_vector_rotation()
        else:
            self.time_is_adjustable = False

    #################################################################################################
    # Methods

    # Method to compute optimal start vector for linear axes # TODO: comment
    def compute_optimal_start_vector_linear_axes(self): 
        
        start_position_linear_axes = self.start_position_linear_axes.get_as_array()
        end_position_linear_axes = self.end_position_linear_axes.get_as_array()

        if self.movement_type in [0, 1]:
            start_vector_linear = end_position_linear_axes - start_position_linear_axes
            vector_length = np.linalg.norm(start_vector_linear)
            if vector_length > 0:
                self.start_vector_linear_axes = start_vector_linear / vector_length * self.feed_rate
            else:
                pass
        else:
            XY_normal_vector = np.array([0.0, 0.0, 1.0])
            arc_center = self.arc_information.get_arc_center_as_array()
            arc_center_2_start = start_position_linear_axes - arc_center
            
            if self.movement_type == 2:
                self.start_vector_linear_axes = vecfunc.compute_normal_vector(arc_center_2_start, XY_normal_vector, "right") * self.feed_rate
            else: 
                self.start_vector_linear_axes = vecfunc.compute_normal_vector(arc_center_2_start, XY_normal_vector, "left") * self.feed_rate

    # TODO
    def compute_optimal_start_vector_rotation(self):
        pass

    # Method to compute optimal end vector for linear axes # TODO: comment    
    def compute_optimal_end_vector_linear_axes(self):
        
        start_position_linear_axes = self.start_position_linear_axes.get_as_array()
        end_position_linear_axes = self.end_position_linear_axes.get_as_array()

        if self.movement_type in [0, 1]:
            end_vector_linear = end_position_linear_axes - start_position_linear_axes
            vector_length = np.linalg.norm(end_vector_linear)
            if vector_length > 0:
                self.end_vector_linear_axes = end_vector_linear / vector_length * self.feed_rate
            else:
                pass
        else:
            XY_normal_vector = np.array([0.0, 0.0, 1.0])
            arc_center = self.arc_information.get_arc_center_as_array()
            arc_center_2_end = end_position_linear_axes - arc_center
            
            if self.movement_type == 2:
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

        if self.movement_type == -1:
            return
        
        start_position_linear_axes = self.start_position_linear_axes.get_as_array()
        end_position_linear_axes = self.end_position_linear_axes.get_as_array()

        target_velocity = self.feed_rate

        if target_velocity == 0:
            raise Exception(f"F value is 0 in line {self.line_index+1}.")
        
        if self.movement_type in [0, 1]:
            distance = np.linalg.norm(end_position_linear_axes - start_position_linear_axes)
        
        else:
            arc_center = self.arc_information.get_arc_center_as_array()

            distance_Z = end_position_linear_axes[2] - start_position_linear_axes[2]

            start_position_linear_axes[2] = 0
            end_position_linear_axes[2] = 0
            arc_center [2] = 0

            center_2_start = start_position_linear_axes - arc_center
            center_2_end = end_position_linear_axes - arc_center

            radius = abs(self.arc_information.radius)

            if self.arc_information.radius >= 0:
                smaller_angle = True
            else:
                smaller_angle = False

            angle: float = vecfunc.compute_angle(center_2_start, center_2_end, smaller_angle)
            
            circumference: float = 2.0*math.pi*radius

            arc_distance: float = angle / 360.0 * circumference
            
            distance = math.sqrt(math.pow(arc_distance, 2) + math.pow(distance_Z, 2))

        self.time = int(distance / target_velocity)

    # Method to get the position of linear axes in a movement at a given time # TODO: comment
    def get_position_linear_axes_in_movement(self, 
                                             time_in_movement: int):

        position = np.array([0.0, 0.0, 0.0])

        portion = time_in_movement / self.time

        start_position_linear_axes = self.start_position_linear_axes.get_as_array()
        end_position_linear_axes = self.end_position_linear_axes.get_as_array()
        
        if self.movement_type == -1:
            position = start_position_linear_axes
        elif self.movement_type in [0, 1]:

            position = start_position_linear_axes + (end_position_linear_axes - start_position_linear_axes) * portion
        else:
            start_point_linear = copy.deepcopy(start_position_linear_axes)
            end_point_linear = copy.deepcopy(end_position_linear_axes)
            arc_center = self.arc_information.get_arc_center_as_array()

            center_2_start = start_point_linear - arc_center
            center_2_end = end_point_linear - arc_center

            start_point_linear[2] = 0
            end_point_linear[2] = 0
            arc_center[2] = 0

            if self.arc_information.radius >= 0:
                smaller_angle = True
            else:
                smaller_angle = False

            angle = vecfunc.compute_angle(center_2_start, center_2_end, smaller_angle)

            current_angle = portion * angle

            if self.movement_type == 2:
                current_angle *= -1

            center_2_start = center_2_start[0:2]
            arc_center = arc_center[0:2]
            XY_position = vecfunc.rotate_2D_vector(center_2_start, arc_center, current_angle)
            
            position[0] = XY_position[0]
            position[1] = XY_position[1]

            distance_Z = self.end_position_linear_axes.Z - self.start_position_linear_axes.Z
            current_Z = self.start_position_linear_axes.Z + portion * distance_Z
            position[2] = current_Z

        return np.round(position, 3)

    # Method to print info of movement # TODO: comment
    def print_info(self):
        print(f"Movement in line {self.line_index+1}")
        print(f"Movement: {self.movement_type}")
        print(f"Start point: {self.start_position_linear_axes.print()}")
        print(f"End point: {self.end_position_linear_axes.print()}")
        print(f"Start vector: {self.start_vector_linear_axes}")
        print(f"End vector: {self.end_vector_linear_axes}")

        if self.movement_type in [2, 3]:
            print(f"Arc info: {self.arc_information.print()}")
        
        print(f"feed rate [mm/ms]: {self.feed_rate}")
        print(f"Expected time: {self.time}")

    def adjust_start_and_total_time(self, 
                                    offset: int, 
                                    factor: float):
        self.start_time = self.start_time * factor + offset
        self.time = self.time * factor


# End of class
#####################################################################################################
