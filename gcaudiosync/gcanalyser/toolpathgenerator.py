from typing import List

import matplotlib
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection

from gcaudiosync.gcanalyser.movementmanager import MovementManager


class ToolPathGenerator:
    """
    Generates and visualizes the toolpath of a CNC machine.

    Attributes:
        visible_tool_path_length (int): Number of visible points on the toolpath for animation.
        string_length (int): Length of the string used to display G-code commands.
        active_g_code_line_index (int): Index of the currently active G-code line.
        delta_time (int): Time between frames in milliseconds.
        fps (float): Frames per second for the animation.
        total_time (int): Total duration of the toolpath in milliseconds.
        nof_frames (int): Total number of frames in the animation.
        tool_path_time (List[float]): List of timestamps for each toolpath point.
        tool_path_X (List[float]): List of X coordinates for each toolpath point.
        tool_path_Y (List[float]): List of Y coordinates for each toolpath point.
        tool_path_Z (List[float]): List of Z coordinates for each toolpath point.
        line_index (List[int]): List of G-code line indices corresponding to each toolpath point.
        g_code (List[str]): List of G-code commands.
        movement_type (List[int]): List of movement types for each toolpath point (TODO: define movement types).
    """

    def __init__(self):
        """
        Initializes the ToolPathGenerator object with default values.
        """

        self.visible_tool_path_length = 200  # visible points of the tool path
        self.string_length = 80

        self.active_g_code_line_index: int = -1
        self.delta_time: int = 0
        self.fps: float = 0
        self.total_time: int = 0
        self.nof_frames: int = 0
        self.tool_path_time: List[float] = []
        self.tool_path_X: List[float] = []
        self.tool_path_Y: List[float] = []
        self.tool_path_Z: List[float] = []
        self.line_index: List[int] = []
        self.g_code: List[str] = []
        self.movement_type: List[int] = []

    # generate all the data needed for the toolpath
    def generate_total_tool_path(
        self, fps: int, Movement_Manager: MovementManager, g_code: list
    ):
        """
        Generates the complete toolpath data.

        Args:
            fps (int): Frames per second for the animation.
            Movement_Manager (MovementManager): Object containing toolpath information.
            g_code (list): List of G-code commands.
        """

        # save parameters
        self.fps = fps
        self.g_code = g_code

        # compute time between two frames
        self.delta_time: float = 1000.0 / self.fps

        # get total time
        self.total_time = Movement_Manager.total_duration

        # compute number of frames
        self.nof_frames = int(self.total_time / self.delta_time)

        # get the active line and position for every frame
        for time_step in range(self.nof_frames):
            # compute current time
            current_time = time_step * self.delta_time

            # get tool path information
            tool_path_information = Movement_Manager.get_tool_path_information(
                current_time
            )
            current_line_index = tool_path_information.g_code_line_index
            current_position_linear_axes = tool_path_information.position_linear_axes
            current_movement_type = tool_path_information.movement_type  # TODO

            self.line_index.append(current_line_index)

            # append the new information
            self.movement_type.append(current_movement_type)
            self.tool_path_time.append(current_time)
            self.tool_path_X.append(current_position_linear_axes[0])
            self.tool_path_Y.append(current_position_linear_axes[1])
            self.tool_path_Z.append(current_position_linear_axes[2])

    # plot tool path version Haas
    def plot_tool_path_Haas(self):
        """
        Generates a temporary plot of the toolpath.
        """

        # set limits of axes
        min_X = min(self.tool_path_X) - 20
        max_X = max(self.tool_path_X) + 20
        min_Y = min(self.tool_path_Y) - 20
        max_Y = max(self.tool_path_Y) + 20

        # get total limits
        min_total = min(min_X, min_Y)
        max_total = max(max_X, max_Y)

        # create a figure and axes
        fig = plt.figure(figsize=(7, 6))
        ax = plt.axes(xlim=(min_total, max_total), ylim=(min_total, max_total))

        # adjust the plot
        plt.subplots_adjust(left=0.1, right=0.75, top=0.95, bottom=0.3)

        # set axes
        ax.set(xlim=[min_X, max_X], ylim=[min_Y, max_Y], xlabel="X", ylabel="Y")

        # create a toolpath to plot
        (tool_path,) = ax.plot(
            self.tool_path_X[0],
            self.tool_path_Y[0],
        )

        # create the tool position to plot
        (tool_position,) = ax.plot(
            self.tool_path_X[0],
            self.tool_path_Y[0],
            "o",
            # label = "",          # maybe add the active tool
            color="red",
        )

        # create the info box on the right of the plot
        props_info_right = dict(boxstyle="round", facecolor="grey", alpha=0.15)
        info_right = ax.text(
            1.05,
            0.8,
            "",
            transform=ax.transAxes,
            verticalalignment="top",
            bbox=props_info_right,
        )

        # create the info boxes under the plot
        props_c_code_text_nonactive = dict(
            boxstyle="round", facecolor="grey", alpha=0.15
        )
        props_c_code_text_active = dict(boxstyle="round", facecolor="red", alpha=0.15)

        g_code_text_above = ax.text(
            0.05,
            -0.15,
            "".ljust(self.string_length),
            transform=ax.transAxes,
            verticalalignment="top",
            bbox=props_c_code_text_nonactive,
        )
        g_code_text_active = ax.text(
            0.05,
            -0.25,
            self.g_code[0].ljust(self.string_length),
            transform=ax.transAxes,
            verticalalignment="top",
            bbox=props_c_code_text_active,
        )
        g_code_text_under = ax.text(
            0.05,
            -0.31,
            self.g_code[1].ljust(self.string_length)
            + "\n"
            + self.g_code[2].ljust(self.string_length),
            transform=ax.transAxes,
            verticalalignment="top",
            bbox=props_c_code_text_nonactive,
        )

        # create a update function for the plot
        def update(frame):
            # set end of visible tool path
            if frame >= self.visible_tool_path_length:
                end_of_visible_tool_path = frame - self.visible_tool_path_length
            else:
                end_of_visible_tool_path = 0

            # update tool_position
            tool_position.set_data(self.tool_path_X[frame], self.tool_path_Y[frame])

            # update tool_path
            if frame > 0:
                tool_path.set_data(
                    self.tool_path_X[end_of_visible_tool_path:frame],
                    self.tool_path_Y[end_of_visible_tool_path:frame],
                )

            # update info on the right of the plot
            time = round(self.delta_time * frame / 1000.0, 3)
            x_position = self.tool_path_X[frame]
            y_position = self.tool_path_Y[frame]
            z_position = self.tool_path_Z[frame]
            info_right_text = (
                "Time = %05.3f s \nX = %+08.3f mm\nY = %+08.3f mm\nZ = %+08.3f mm"
                % (time, x_position, y_position, z_position)
            )
            info_right.set_text(info_right_text)

            # update info under the plot if active line has changed
            if self.active_g_code_line_index != self.line_index[frame]:
                self.active_g_code_line_index = self.line_index[frame]
                active_g_code_line = self.active_g_code_line_index

                g_code_text_active.set_text(
                    self.g_code[active_g_code_line].ljust(self.string_length)
                )

                if active_g_code_line == 0:
                    pass
                elif active_g_code_line == 1:
                    g_code_text_above.set_text(
                        "".ljust(self.string_length)
                        + "\n"
                        + self.g_code[active_g_code_line - 1].ljust(self.string_length)
                    )
                    g_code_text_under.set_text(
                        self.g_code[active_g_code_line + 1].ljust(self.string_length)
                        + "\n"
                        + self.g_code[active_g_code_line + 2].ljust(self.string_length)
                    )
                elif active_g_code_line == len(self.g_code) - 2:
                    g_code_text_above.set_text(
                        self.g_code[active_g_code_line - 2].ljust(self.string_length)
                        + "\n"
                        + self.g_code[active_g_code_line - 1].ljust(self.string_length)
                    )
                    g_code_text_under.set_text(
                        self.g_code[active_g_code_line + 1].ljust(self.string_length)
                        + "\n"
                        + "".ljust(self.string_length)
                    )
                elif active_g_code_line == len(self.g_code) - 1:
                    g_code_text_above.set_text(
                        "".ljust(self.string_length)
                        + "\n"
                        + self.g_code[active_g_code_line - 1].ljust(self.string_length)
                    )
                    g_code_text_under.set_text(
                        "".ljust(self.string_length)
                        + "\n"
                        + "".ljust(self.string_length)
                    )
                else:
                    g_code_text_above.set_text(
                        self.g_code[active_g_code_line - 2].ljust(self.string_length)
                        + " \n"
                        + self.g_code[active_g_code_line - 1].ljust(self.string_length)
                    )
                    g_code_text_under.set_text(
                        self.g_code[active_g_code_line + 1].ljust(self.string_length)
                        + "\n"
                        + self.g_code[active_g_code_line + 2].ljust(self.string_length)
                    )

            return tuple([tool_path]) + tuple([info_right])

        ani = animation.FuncAnimation(
            fig=fig,
            func=update,
            frames=len(self.tool_path_time),
            interval=self.delta_time,
        )

        plt.show()

    # plot tool path version Mueller
    def plot_tool_path_Mueller(self):
        """
        Generates a storable plot of the toolpath.
        """

        # set limits of axes
        min_X = min(self.tool_path_X) - 20
        max_X = max(self.tool_path_X) + 20
        min_Y = min(self.tool_path_Y) - 20
        max_Y = max(self.tool_path_Y) + 20

        # get total limits
        min_total = min(min_X, min_Y)
        max_total = max(max_X, max_Y)

        # create a figure and axes
        fig = plt.figure(figsize=(7, 6))
        ax = plt.axes(xlim=(min_total, max_total), ylim=(min_total, max_total))

        # adjust the plot
        plt.subplots_adjust(left=0.1, right=0.75, top=0.95, bottom=0.3)

        # set axes
        ax.set(xlim=[min_X, max_X], ylim=[min_Y, max_Y], xlabel="X", ylabel="Y")

        # create a toolpath to plot
        (tool_path,) = ax.plot(
            self.tool_path_X[0],
            self.tool_path_Y[0],
        )

        # create the tool position to plot
        (tool_position,) = ax.plot(
            self.tool_path_X[0],
            self.tool_path_Y[0],
            "o",
            # label = "",          # maybe add the active tool
            color="red",
        )

        # create the info box on the right of the plot
        props_info_right = dict(boxstyle="round", facecolor="grey", alpha=0.15)
        info_right = ax.text(
            1.05,
            0.8,
            "",
            transform=ax.transAxes,
            verticalalignment="top",
            bbox=props_info_right,
        )

        # create the info boxes under the plot
        props_c_code_text_nonactive = dict(
            boxstyle="round", facecolor="grey", alpha=0.15
        )
        props_c_code_text_active = dict(boxstyle="round", facecolor="red", alpha=0.15)

        g_code_text_above = ax.text(
            0.05,
            -0.15,
            "".ljust(self.string_length),
            transform=ax.transAxes,
            verticalalignment="top",
            bbox=props_c_code_text_nonactive,
        )
        g_code_text_active = ax.text(
            0.05,
            -0.25,
            self.g_code[0].ljust(self.string_length),
            transform=ax.transAxes,
            verticalalignment="top",
            bbox=props_c_code_text_active,
        )
        g_code_text_under = ax.text(
            0.05,
            -0.31,
            self.g_code[1].ljust(self.string_length)
            + "\n"
            + self.g_code[2].ljust(self.string_length),
            transform=ax.transAxes,
            verticalalignment="top",
            bbox=props_c_code_text_nonactive,
        )

        # create a update function for the plot
        def update(frame):
            # set end of visible tool path
            if frame >= self.visible_tool_path_length:
                end_of_visible_tool_path = frame - self.visible_tool_path_length
            else:
                end_of_visible_tool_path = 0

            # update tool_position
            tool_position.set_data(self.tool_path_X[frame], self.tool_path_Y[frame])

            # update tool_path
            if frame > 0:
                tool_path.set_data(
                    self.tool_path_X[end_of_visible_tool_path:frame],
                    self.tool_path_Y[end_of_visible_tool_path:frame],
                )

            # update info on the right of the plot
            time = round(self.delta_time * frame / 1000.0, 3)
            x_position = self.tool_path_X[frame]
            y_position = self.tool_path_Y[frame]
            z_position = self.tool_path_Z[frame]
            info_right_text = (
                "Time = %05.3f s \nX = %+08.3f mm\nY = %+08.3f mm\nZ = %+08.3f mm"
                % (time, x_position, y_position, z_position)
            )
            info_right.set_text(info_right_text)

            # update info under the plot if active line has changed
            if self.active_g_code_line_index != self.line_index[frame]:
                self.active_g_code_line_index = self.line_index[frame]
                active_g_code_line = self.active_g_code_line_index

                g_code_text_active.set_text(
                    self.g_code[active_g_code_line].ljust(self.string_length)
                )

                if active_g_code_line == 0:
                    pass
                elif active_g_code_line == 1:
                    g_code_text_above.set_text(
                        "".ljust(self.string_length)
                        + "\n"
                        + self.g_code[active_g_code_line - 1].ljust(self.string_length)
                    )
                    g_code_text_under.set_text(
                        self.g_code[active_g_code_line + 1].ljust(self.string_length)
                        + "\n"
                        + self.g_code[active_g_code_line + 2].ljust(self.string_length)
                    )
                elif active_g_code_line == len(self.g_code) - 2:
                    g_code_text_above.set_text(
                        self.g_code[active_g_code_line - 2].ljust(self.string_length)
                        + "\n"
                        + self.g_code[active_g_code_line - 1].ljust(self.string_length)
                    )
                    g_code_text_under.set_text(
                        self.g_code[active_g_code_line + 1].ljust(self.string_length)
                        + "\n"
                        + "".ljust(self.string_length)
                    )
                elif active_g_code_line == len(self.g_code) - 1:
                    g_code_text_above.set_text(
                        "".ljust(self.string_length)
                        + "\n"
                        + self.g_code[active_g_code_line - 1].ljust(self.string_length)
                    )
                    g_code_text_under.set_text(
                        "".ljust(self.string_length)
                        + "\n"
                        + "".ljust(self.string_length)
                    )
                else:
                    g_code_text_above.set_text(
                        self.g_code[active_g_code_line - 2].ljust(self.string_length)
                        + " \n"
                        + self.g_code[active_g_code_line - 1].ljust(self.string_length)
                    )
                    g_code_text_under.set_text(
                        self.g_code[active_g_code_line + 1].ljust(self.string_length)
                        + "\n"
                        + self.g_code[active_g_code_line + 2].ljust(self.string_length)
                    )

            return tuple([tool_path]) + tuple([info_right])

        ani = animation.FuncAnimation(
            fig=fig,
            func=update,
            frames=len(self.tool_path_time),
            interval=self.delta_time,
        )

        plt.show()

        # Bitte noch das abspeichern hinzufuegen


class AlternativeToolPathAnimator:
    def __init__(
        self,
        movement_manager: MovementManager,
        g_code: list[str],
        ax_tool: matplotlib.axes.Axes,
        ax_info: matplotlib.axes.Axes,
        t_max: float,
        fps: int = 26,
        padding: float = 10,
        n_points_visible: int = 200,
        string_length: int = 20,
        n_texts: int = 5,
    ) -> None:
        # Save params
        self.mm = movement_manager
        self.g_code = g_code
        self.fps = fps
        self.n_points_visible = n_points_visible
        self.string_length = string_length
        self.n_texts = n_texts

        # Setup timing params
        self.frame_delta_time: float = 1 / self.fps
        self.total_time = t_max
        self.nof_frames = int(self.total_time / self.frame_delta_time)

        # Precalculate the tool path once to extract limits
        tool_path = np.array(
            [
                self._get_position_linear_axes_save(1000 * t)
                for t in np.linspace(0, self.total_time, self.nof_frames)
            ]
        )

        # Extract the limits
        max_x = np.nanmax(tool_path[:, 0])
        max_y = np.nanmax(tool_path[:, 1])
        min_x = np.nanmin(tool_path[:, 0])
        min_y = np.nanmin(tool_path[:, 1])

        # Setup tool axes for the plot
        ax_tool.axis("equal")
        ax_tool.set_aspect("equal", "box")
        ax_tool.set_xlim(min_x - padding, max_x + padding)
        ax_tool.set_ylim(min_y - padding, max_y + padding)
        ax_tool.set_xlabel("X in mm")
        ax_tool.set_ylabel("Y in mm")

        # Setup info axes for the plot
        ax_info.axis("off")
        ax_info.set_xlim(0, 1)
        ax_info.set_ylim(-3, 2 * self.n_texts + 0.5)

        # Create the tool path line
        (self.tool_path_line,) = ax_tool.plot([], [])

        # Create the tool position point
        (self.tool_position_line,) = ax_tool.plot([], [], "o", color="red")

        # Create the infos
        extra_args = dict(
            horizontalalignment="left",
            verticalalignment="center",
            fontsize=10,
            fontname="monospace",
            color="gray",
        )
        self.texts = [
            ax_info.text(0, i, "", **extra_args) for i in range(2 * self.n_texts + 1)
        ]
        self.texts[self.n_texts].set_color("red")

        # Create info box
        self.info_box = ax_info.text(
            0,
            -1,
            "",
            # transform=ax_tool.transAxes,
            verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="grey", alpha=0.15),
        )

    def _get_position_linear_axes_save(self, t_ms: float) -> float:
        try:
            return self.mm.get_tool_path_information(t_ms).position_linear_axes
        except Exception:
            return np.nan, np.nan, np.nan

    def _gen_text(self, t_ms: float, i: int) -> str:
        try:
            tool_path_information = self.mm.get_tool_path_information(t_ms)
            text = self.g_code[tool_path_information.g_code_line_index + i]
        except Exception:
            return ""
        if len(text) > self.string_length:
            return f"{text[:self.string_length-3]}..."
        return text

    def callback(
        self, frame_s: float
    ) -> tuple[matplotlib.lines.Line2D, matplotlib.lines.Line2D, LineCollection]:
        # Convert the frame time to milliseconds
        frame_ms = frame_s * 1000

        # Calculate the current position of the tool
        x_now, y_now, z_now = self._get_position_linear_axes_save(frame_ms)

        # Retrieve previous data
        x_was = self.tool_path_line.get_xdata()
        y_was = self.tool_path_line.get_ydata()

        # Concat the new data to the previous data and clip to the last 200 points
        x_new = np.concatenate([x_was, [x_now]])[-self.n_points_visible :]
        y_new = np.concatenate([y_was, [y_now]])[-self.n_points_visible :]

        # Update the tool position
        self.tool_path_line.set_data(x_new, y_new)

        # Update the tool position point
        self.tool_position_line.set_data(x_now, y_now)

        # Update the info text
        for i, text in enumerate(self.texts[::-1]):
            new_text = self._gen_text(frame_ms, i - self.n_texts)
            text.set_text(new_text)

        # Update the info box
        info_box_text = (
            "Time = %05.3f s \nX = %+08.3f mm\nY = %+08.3f mm\nZ = %+08.3f mm"
            % (frame_s, x_now, y_now, z_now)
        )
        self.info_box.set_text(info_box_text)

        return self.tool_path_line, self.tool_position_line, *self.texts, self.info_box

    def run(self):
        frames = np.linspace(0, self.total_time, self.nof_frames)
        time_diff_in_millis = 1000 / self.fps
        animation.FuncAnimation(
            self.tool_path_line.get_figure(),
            self.callback,
            frames=frames,
            blit=False,
            interval=time_diff_in_millis,
            repeat=False,
        )
        plt.show()
