from gcaudiosync.gcanalyser.movementmanager import Movement_Manager

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class Tool_Path_Generator:

    def __init__(self):
        self.visible_tool_path_length = 200          # visible points of the tool path
        self.string_length = 80

        self.active_g_code_line_index: int = -1
        self.delta_time: int = 0
        self.fps: float = 0
        self.total_time: int = 0
        self.nof_frames: int = 0
        self.tool_path_time:list = []
        self.tool_path_X:list = []
        self.tool_path_Y:list = []
        self.tool_path_Z: list = []
        self.line_index:list = []
        self.g_code: list = []

    # generate all the data needed for the toolpath
    def generate_total_tool_path(self, 
                                 fps: int, 
                                 Movement_Manager: Movement_Manager, 
                                 g_code: list):

        # save parameters
        self.fps = fps
        self.g_code = g_code

        # compute time between two frames
        self.delta_time: float = 1000.0 / self.fps
        
        # get total time
        self.total_time = Movement_Manager.total_time

        # compute number of frames
        self.nof_frames = int(self.total_time / self.delta_time)

        # get the active line and position for every frame
        for time_step in range(self.nof_frames):
            
            # compute current time
            current_time = time_step * self.delta_time

            # get current index and position
            current_index, current_position = Movement_Manager.get_plot_info(current_time)

            #current_index = Movement_Manager.get_line_index_at_time(current_time)
            self.line_index.append(current_index)
            
            # append the new information
            self.tool_path_time.append(current_time)
            self.tool_path_X.append(current_position[0])
            self.tool_path_Y.append(current_position[1])
            self.tool_path_Z.append(current_position[2])

    # plot tool path
    def plot_tool_path(self):
        
        # set limits of axes
        min_X = min(self.tool_path_X) - 20
        max_X = max(self.tool_path_X) + 20
        min_Y = min(self.tool_path_Y) - 20
        max_Y = max(self.tool_path_Y) + 20 

        # get total limits
        min_total = min(min_X, min_Y)
        max_total = max(max_X, max_Y)
        
        # create a figure and axes
        fig = plt.figure(figsize = (7,6))
        ax = plt.axes(xlim=(min_total, max_total), 
                      ylim=(min_total, max_total))
        
        # adjust the plot
        plt.subplots_adjust(left = 0.1, 
                            right = 0.75,
                            top = 0.95,
                            bottom = 0.3)
        
        # set axes
        ax.set(xlim = [min_X, max_X], 
               ylim = [min_Y, max_Y], 
               xlabel = "X", 
               ylabel = "Y")
        
        # show legend
        # ax.legend()

        # create a toolpath to plot
        tool_path, = ax.plot(self.tool_path_X[0], 
                             self.tool_path_X[0], 
                             # label = "",
                             )
        
        # create the tool position to plot
        tool_position, = ax.plot(self.tool_path_X[0], 
                                 self.tool_path_X[0], 
                                 "o",
                                 # label = "",          # maybe add the active tool
                                 color = "red")
        
        # create the info box on the right of the plot
        props_info_right = dict(boxstyle = 'round', facecolor = 'grey', alpha = 0.15) 
        info_right = ax.text(1.05, 0.8, "", transform = ax.transAxes, verticalalignment='top', bbox = props_info_right)

        # create the info boxes under the plot
        props_c_code_text_nonactive = dict(boxstyle = 'round', facecolor = 'grey', alpha = 0.15) 
        props_c_code_text_active = dict(boxstyle = 'round', facecolor = 'red', alpha = 0.15) 

        g_code_text_above  = ax.text(0.05, 
                                     -0.15, 
                                     "".ljust(self.string_length), 
                                     transform = ax.transAxes, 
                                     verticalalignment = 'top', 
                                     bbox = props_c_code_text_nonactive)
        g_code_text_active = ax.text(0.05, 
                                     -0.25, 
                                     self.g_code[0].ljust(self.string_length), 
                                     transform = 
                                     ax.transAxes, 
                                     verticalalignment = 'top', 
                                     bbox = props_c_code_text_active)
        g_code_text_under  = ax.text(0.05, 
                                     -0.31, 
                                     self.g_code[1].ljust(self.string_length) + "\n" + self.g_code[2].ljust(self.string_length), 
                                     transform = ax.transAxes, 
                                     verticalalignment = 'top', 
                                     bbox = props_c_code_text_nonactive)

        # create a update function for the plot
        def update(frame):
            
            # set end of visible tool path
            if frame >= self.visible_tool_path_length: 
                end_of_visible_tool_path = frame - self.visible_tool_path_length
            else:
                end_of_visible_tool_path = 0
            
            # update tool_position
            tool_position.set_data(self.tool_path_X[frame], 
                                   self.tool_path_Y[frame])

            # update tool_path
            if frame > 0:
                tool_path.set_data(self.tool_path_X[end_of_visible_tool_path:frame], 
                                   self.tool_path_Y[end_of_visible_tool_path:frame])

            # update info on the right of the plot
            time = round(self.delta_time * frame / 1000.0, 3)
            x_position = self.tool_path_X[frame]
            y_position = self.tool_path_Y[frame]
            z_position = self.tool_path_Z[frame]
            info_right_text = "Time = %05.3f s \nX = %+08.3f mm\nY = %+08.3f mm\nZ = %+08.3f mm" % (time, x_position, y_position, z_position)
            info_right.set_text(info_right_text)
            
            # update info under the plot if active line has changed
            if self.active_g_code_line_index != self.line_index[frame]:
                self.active_g_code_line_index = self.line_index[frame]
                active_g_code_line = self.active_g_code_line_index

                g_code_text_active.set_text(self.g_code[active_g_code_line].ljust(self.string_length))

                if active_g_code_line == 0:
                    pass
                elif active_g_code_line == 1:
                    g_code_text_above.set_text("".ljust(self.string_length) + "\n"  +
                                               self.g_code[active_g_code_line - 1].ljust(self.string_length))
                    g_code_text_under.set_text(self.g_code[active_g_code_line + 1].ljust(self.string_length) + "\n" +
                                               self.g_code[active_g_code_line + 2].ljust(self.string_length))
                elif active_g_code_line == len(self.g_code) - 2:
                    g_code_text_above.set_text(self.g_code[active_g_code_line - 2].ljust(self.string_length) + "\n" +
                                               self.g_code[active_g_code_line - 1].ljust(self.string_length))
                    g_code_text_under.set_text(self.g_code[active_g_code_line + 1].ljust(self.string_length) + "\n" +
                                               "".ljust(self.string_length))
                elif active_g_code_line == len(self.g_code) - 1:
                    g_code_text_above.set_text("".ljust(self.string_length) + "\n"+
                                               self.g_code[active_g_code_line-1].ljust(self.string_length))
                    g_code_text_under.set_text("".ljust(self.string_length) + "\n" +
                                               "".ljust(self.string_length))
                else:
                    g_code_text_above.set_text(self.g_code[active_g_code_line-2].ljust(self.string_length) + " \n"+
                                               self.g_code[active_g_code_line-1].ljust(self.string_length))
                    g_code_text_under.set_text(self.g_code[active_g_code_line + 1].ljust(self.string_length) + "\n" +
                                               self.g_code[active_g_code_line + 2].ljust(self.string_length))

            return tuple([tool_path]) + tuple([info_right])


        ani = animation.FuncAnimation(fig = fig, 
                                      func = update, 
                                      frames = len(self.tool_path_time), 
                                      interval = self.delta_time)

        plt.show()