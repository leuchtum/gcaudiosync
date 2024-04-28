import numpy as np
import copy

from gcaudiosync.gcanalyser.movement import Movement
from gcaudiosync.gcanalyser.cncstatus import CNC_Status

class Movement_Manager:

    # counter = 0

    movements: Movement = []

    def __init__(self, first_line_status: CNC_Status):

        movement = Movement(line_index = -1, 
                            movement = 0, 
                            start_point_linear = first_line_status.position_linear, 
                            end_point_linear = first_line_status.position_linear,
                            start_point_rotation = first_line_status.position_rotation,
                            end_point_rotation = first_line_status.position_rotation, 
                            info_arc=None)
        
        self.movements.append(movement)

    def add_linear_movement(self, 
                            index: int, 
                            last_line_status: CNC_Status,
                            line_status: CNC_Status):
        
        # for debugging
        # self.counter += 1
        # print("Movement_Manager call no. " +  str(self.counter) + ": linear movement in line " + str(index))

        return 0 # time

    def add_arc_movement(self, 
                         index: int, 
                         last_line_status: CNC_Status,
                         line_status: CNC_Status):
        
        # for debugging
        # self.counter += 1
        # print("Movement_Manager call no. " +  str(self.counter) + ": arc movement in line " + str(index))

        return 0 # time

    def add_tool_change(self, index: int):
        # for debugging
        # self.counter += 1
        # print("Movement_Manager call no. " +  str(self.counter) + ": tool change in line " + str(index))

        return 0 # time
    
    def add_pause(self, index: int, time: int):

        last_movement:Movement = copy.deepcopy(self.movements[-1])

        movement = Movement(line_index = -1, 
                            movement = 0, 
                            start_point_linear = last_movement.start_point_linear, 
                            end_point_linear = last_movement.end_point_linear,
                            start_point_rotation = last_movement.start_point_rotation,
                            end_point_rotation = last_movement.end_point_rotation, 
                            info_arc=None)
        
        self.update_last_movement(movement)

        self.movements.append(movement)

    def update_connection_of_movements(self, movement: Movement):
        pass