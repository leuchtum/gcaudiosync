from gcaudiosync.gcanalyser.movementmanager import Movement_Manager

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class Tool_Path_Generator:

    def __init__(self):
        self.tool_path_time = []
        self.tool_path_X = []
        self.tool_path_Y = []
        self.tool_path_Z = []

    def generate_tool_path(self, expected_time_total, Movement_Manager: Movement_Manager):

        delta_time = 100    # [ms]
        nof_steps = int(expected_time_total / delta_time)

        for time_step in range(nof_steps):

            current_time = time_step * delta_time

            current_position = Movement_Manager.get_position_linear(current_time)

            current_X = current_position[0]
            current_Y = current_position[1]
            current_Z = current_position[2]

            self.tool_path_time.append(current_time)
            self.tool_path_X.append(current_X)
            self.tool_path_Y.append(current_Y)
            self.tool_path_Z.append(current_Z)


        fig, ax = plt.subplots()

        line = ax.plot(self.tool_path_X[0], self.tool_path_Y[0], label=f"tool path")[0]
        ax.set(xlim = [-110, 110], ylim = [-110, 110], xlabel = "X", ylabel = "Y")
        ax.legend()


        def update(frame):

            # update the line plot:
            line.set_xdata(self.tool_path_X[:frame])
            line.set_ydata(self.tool_path_Y[:frame])
            return (line)


        ani = animation.FuncAnimation(fig = fig, 
                                      func = update, 
                                      frames = len(self.tool_path_time), 
                                      interval = delta_time)
        plt.show()

        
