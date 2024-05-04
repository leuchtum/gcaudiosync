import numpy as np
import copy
import math
import gcaudiosync.gcanalyser.vectorfunctions as vecfunc

class Movement:

    expected_time = 0

    start_vector_linear = np.array([0.0, 0.0, 0.0])
    end_vector_linear = np.array([0.0, 0.0, 0.0])

    start_vector_rotation = np.array([0.0, 0.0, 0.0])
    end_vector_rotation = np.array([0.0, 0.0, 0.0])

    def __init__(self,
                 line_index: int,
                 movement = -1,
                 start_point_linear = np.array([0.0, 0.0, 0.0]), 
                 end_point_linear = np.array([0.0, 0.0, 0.0]),
                 start_point_rotation = np.array([0.0, 0.0, 0.0]),
                 end_point_rotation = np.array([0.0, 0.0, 0.0]),
                 info_arc = None,
                 feed_rate = 0):
        
        self.line_index = line_index

        self.movement = movement

        self.start_point_linear = start_point_linear
        self.end_point_linear = end_point_linear

        self.start_point_rotation = start_point_rotation
        self.end_point_rotation = end_point_rotation

        self.info_arc = info_arc         # [direction, I, J, K, R, #turns]

        self.feed_rate = feed_rate

        if movement != -1:
            self.compute_optimal_start_vector_linear()
            self.compute_optimal_start_vector_rotation()
            self.compute_optimal_end_vector_linear()
            self.compute_optimal_end_vector_rotation()
            self.compute_expected_time()

    def compute_optimal_start_vector_linear(self):
        
        if self.movement in [0, 1]:
            start_vector_linear = self.end_point_linear - self.start_point_linear
            vector_length = np.linalg.norm(start_vector_linear)
            if vector_length > 0:
                self.start_vector_linear = start_vector_linear / vector_length * self.feed_rate
            else:
                pass
        else:
            XY_normal_vector = np.array([0.0, 0.0, 1.0])
            arc_center = self.info_arc[1:4]
            arc_center_2_start = self.start_point_linear - arc_center
            
            if self.movement == 2:
                self.start_vector_linear = vecfunc.compute_normal_vector(arc_center_2_start, XY_normal_vector, "right") * self.feed_rate
            else: 
                self.start_vector_linear = vecfunc.compute_normal_vector(arc_center_2_start, XY_normal_vector, "left") * self.feed_rate

    # TODO
    def compute_optimal_start_vector_rotation(self):
        pass

    def compute_optimal_end_vector_linear(self):
        
        if self.movement in [0, 1]:
            end_vector_linear = self.end_point_linear - self.start_point_linear
            vector_length = np.linalg.norm(end_vector_linear)
            if vector_length > 0:
                self.end_vector_linear = end_vector_linear / vector_length * self.feed_rate
            else:
                pass
        else:
            XY_normal_vector = np.array([0.0, 0.0, 1.0])
            arc_center = self.info_arc[1:4]
            arc_center_2_end = self.end_point_linear - arc_center
            
            if self.movement == 2:
                self.end_vector_linear = vecfunc.compute_normal_vector(arc_center_2_end, XY_normal_vector, "right") * self.feed_rate
            else: 
                self.end_vector_linear = vecfunc.compute_normal_vector(arc_center_2_end, XY_normal_vector, "left") * self.feed_rate

    # TODO
    def compute_optimal_end_vector_rotation(self):
        pass

    def do_exact_stop(self):
        self.end_vector_linear = np.array([0.0, 0.0, 0.0])
        self.end_vector_rotation = np.array([0.0, 0.0, 0.0])

    def compute_expected_time(self):

        if self.movement == -1:
            return self.expected_time
        
        # start_velocity_linear = np.linalg.norm(self.start_vector_linear)
        # end_velocity_linear = np.linalg.norm(self.end_Vector_linear)

        target_velocity = self.feed_rate

        if target_velocity == 0:
            raise Exception("Hier ist F = 0.")
        
        if self.movement in [0, 1]:
            distance = np.linalg.norm(self.end_point_linear - self.start_point_linear)
        
        else:

            start_point_linear = copy.deepcopy(self.start_point_linear)
            end_point_linear = copy.deepcopy(self.end_point_linear)
            arc_center = copy.deepcopy(self.info_arc[1:4])

            center_2_start = start_point_linear - arc_center
            center_2_end = end_point_linear - arc_center

            distance_Z = end_point_linear[2] - start_point_linear[2]

            start_point_linear[2] = 0
            end_point_linear[2] = 0

            radius = abs(self.info_arc[4])
            turns = self.info_arc[5]

            if self.info_arc[4] >= 0:
                smaller_angle = True
            else:
                smaller_angle = False

            angle = vecfunc.compute_angle(center_2_start, center_2_end, smaller_angle)

            circumference = 2*math.pi*radius

            arc_distance: float = (turns + angle / 360.0) * circumference
            
            distance = math.sqrt(math.pow(arc_distance, 2) + math.pow(distance_Z, 2))

        self.expected_time = distance / target_velocity

    def get_position_in_movement(self, time_in_movement):

        position = np.array([0.0, 0.0, 0.0])

        if self.movement == -1:
            position = self.start_point_linear
        elif self.movement in [0, 1]:
            position = self.start_point_linear + self.start_vector_linear * time_in_movement
        else:
            start_point_linear = copy.deepcopy(self.start_point_linear)
            end_point_linear = copy.deepcopy(self.end_point_linear)
            arc_center = copy.deepcopy(self.info_arc[1:4])

            center_2_start = start_point_linear - arc_center
            center_2_end = end_point_linear - arc_center

            start_point_linear[2] = 0
            end_point_linear[2] = 0

            radius = abs(self.info_arc[4])
            turns = self.info_arc[5]

            if self.info_arc[4] >= 0:
                smaller_angle = True
            else:
                smaller_angle = False

            angle = vecfunc.compute_angle(center_2_start, center_2_end, smaller_angle)

            total_angle = angle + 360.0 * turns

            portion = self.expected_time / time_in_movement

            current_angle = portion * total_angle

            if self.movement == 2:
                current_angle *= -1

            center_2_start = center_2_start[0:2]
            arc_center = arc_center[0:2]
            XY_position = vecfunc.rotate_2D_vector(center_2_start, arc_center, current_angle)
            
            position[0] = XY_position[0]
            position[1] = XY_position[1]

            distance_Z = end_point_linear[2] - start_point_linear[2]
            current_Z = start_point_linear[2] + portion * distance_Z
            position[2] = current_Z

        return position

    def print_info(self):
        print(f"Movement in line {self.line_index}")
        print(f"Movement: {self.movement}")
        print(f"Start point: {self.start_point_linear}")
        print(f"End point: {self.end_point_linear}")
        print(f"Start vector: {self.start_vector_linear}")
        print(f"End vector: {self.end_vector_linear}")

        if self.movement in [2, 3]:
            print(f"Arc info: {self.info_arc}")
        
        print(f"feed rate [mm/ms]: {self.feed_rate}")
        print(f"Expected time: {self.expected_time}")
