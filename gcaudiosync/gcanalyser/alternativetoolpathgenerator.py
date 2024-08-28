import numpy as np
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.artist import Artist
from matplotlib.axes import Axes

from gcaudiosync.gcanalyser.movementmanager import MovementManager


class AlternativeToolPathAnimator:
    def __init__(
        self,
        movement_manager: MovementManager,
        g_code: list[str],
        ax_tool: Axes,
        ax_info: Axes,
        t_max: float,
        fps: int = 26,
        padding: float = 10,
        sec_points_visible: float = 60,
        string_length: int = 30,
        n_texts: int = 7,
    ) -> None:
        # Save params
        self.mm = movement_manager
        self.g_code = g_code
        self.fps = fps
        self.n_points_visible = int(fps * sec_points_visible)
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
        self.texts = [
            ax_info.text(
                0,
                i,
                "",
                horizontalalignment="left",
                verticalalignment="center",
                fontsize=10,
                fontname="monospace",
                color="gray",
            )
            for i in range(2 * self.n_texts + 1)
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

    def _get_position_linear_axes_save(self, t_ms: float) -> tuple[float, float, float]:
        """Helper function to get the position of the tool at a given time."""
        try:
            return self.mm.get_tool_path_information(t_ms).position_linear_axes
        except Exception:
            pass

        _, last_valid_timestamp = self.mm.get_time_stamps()[-1]
        try:
            return self.mm.get_tool_path_information(
                last_valid_timestamp
            ).position_linear_axes
        except Exception:
            pass

        return np.nan, np.nan, np.nan

    def _gen_text(self, t_ms: float, i: int) -> str:
        """Helper function to generate the text for the info box."""
        try:
            path_info = self.mm.get_tool_path_information(t_ms)
            idx = path_info.g_code_line_index + i
        except Exception:
            idx = len(self.g_code) + i

        if idx < 0 or idx >= len(self.g_code):
            return ""

        text = f"{idx:04d}: {self.g_code[idx]}"

        if len(text) > self.string_length:
            return f"{text[:self.string_length-3]}..."

        return text

    def callback(self, frame_s: float) -> tuple[Artist, ...]:
        """Callback function for the animation."""
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
        self.tool_position_line.set_data([x_now], [y_now])

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

    def run(self) -> None:
        """Run the animation."""
        frames = np.linspace(0, self.total_time, self.nof_frames)
        time_diff_in_millis = 1000 / self.fps
        fig = self.tool_path_line.get_figure()
        if fig is None:
            raise ValueError("The tool path line is not attached to a figure.")
        FuncAnimation(
            fig,
            self.callback,
            frames=frames,
            blit=False,
            interval=time_diff_in_millis,
            repeat=False,
        )
        plt.show()
