import numpy as np

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
        pass