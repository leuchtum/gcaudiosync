from dataclasses import dataclass
from typing import Callable, Protocol

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt


@dataclass
class BoundedFunction:
    """
    Represents a bounded function with a start and end x.

    Attributes:
        start (float): The start time of the bounded function.
        end (float): The end time of the bounded function.
        func (Callable[[npt.NDArray[np.float64]], npt.NDArray[np.float64]]): The function to be applied within the bounds.
    """

    start: float
    end: float
    func: Callable[[npt.NDArray[np.float64]], npt.NDArray[np.float64]]

    def condition(self, x: npt.NDArray[np.float64]) -> npt.NDArray[np.bool_]:
        """
        Check if each element in the input array falls within the bounds of the function.

        Args:
            x (npt.NDArray[np.float64]): The array of values to check.

        Returns:
            npt.NDArray[np.bool_]: A boolean array indicating whether each element in the input array falls within the bounds of the function.
        """
        return (x >= self.start) & (x < self.end)


class SegmentBuilder(Protocol):
    """
    A protocol for building segments of bounded functions.
    """

    def __call__(
        self, y0: float, y1: float, x0: float, x1: float
    ) -> list[BoundedFunction]:
        """
        Build a segment of bounded functions.

        Parameters:
        - y0 (float): The starting y of the segment.
        - y1 (float): The ending y of the segment.
        - x0 (float): The starting x of the segment.
        - x1 (float): The ending x of the segment.

        Returns:
        - list[BoundedFunction]: A list of bounded functions representing the segment.
        """
        ...


@dataclass
class LinearSegmentBuilder:
    """
    A class that builds linear segments of bounded functions.
    """

    def __call__(
        self, y0: float, y1: float, x0: float, x1: float
    ) -> list[BoundedFunction]:
        dt = x1 - x0
        if dt == 0:
            return []
        slope = (y1 - y0) / dt
        return [BoundedFunction(x0, x1, lambda t: y0 + slope * (t - x0))]


@dataclass
class PleateauSegmentBuilder:
    """
    A class that builds plateau segments of bounded functions.
    """

    def __call__(
        self, _: float, y1: float, x0: float, x1: float
    ) -> list[BoundedFunction]:
        dx = x1 - x0
        if dx == 0:
            return []
        return [BoundedFunction(x0, x1, lambda _: np.array(y1))]


class BendedSegmentBuilder:
    """
    A class that builds a list of bounded functions representing a bended segment.
    """

    def __init__(self, *, ramp_up_slope: float, ramp_down_slope: float) -> None:
        """
        Initializes a Piecewise object with the specified ramp up and ramp down slopes.

        Args:
            ramp_up_slope (float): The slope of the ramp up segment. Must be non-negative.
            ramp_down_slope (float): The slope of the ramp down segment. Must be non-positive.

        Raises:
            ValueError: If ramp_up_slope is negative or ramp_down_slope is positive.

        Returns:
            None
        """
        if not (ramp_up_slope >= 0 and ramp_down_slope <= 0):
            msg = "ramp_up_slope must be non-negative and ramp_down_slope must be non-positive"
            raise ValueError(msg)
        self.ramp_up_slope = ramp_up_slope
        self.ramp_down_slope = ramp_down_slope

    def __call__(
        self, y0: float, y1: float, x0: float, x1: float
    ) -> list[BoundedFunction]:
        dt = x1 - x0
        if dt == 0:
            return []

        # Determine the slope of the linear part
        slope = self.ramp_up_slope if y1 > y0 else self.ramp_down_slope

        # slope zero means no bend is needed
        if slope == 0:
            return [*PleateauSegmentBuilder()(y0, y1, x0, x1)]

        # From here on the slope is non-zero, thus a bend is needed
        x_bend = x0 + (y1 - y0) / slope
        return [
            *LinearSegmentBuilder()(y0, y1, x0, x_bend),
            *PleateauSegmentBuilder()(y1, y1, x_bend, x1),
        ]


@dataclass(frozen=True)
class ParamizedFormFunc:
    """
    A callable class that represents a parametrized form function.

    This class takes a list of bounded functions and evaluates them based on the given time parameter.

    Attributes:
        bounded_funcs (list[BoundedFunction]): A list of bounded functions.
    """

    bounded_funcs: list[BoundedFunction]

    def __call__(self, samples: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
        """
        Evaluates the bounded functions based at given samples.

        Args:
            samples (npt.ArrayLike): The sample array for evaluation.

        Returns:
            npt.ArrayLike: The evaluated result based on the bounded functions.

        """
        return np.piecewise(
            samples,
            [bf.condition(samples) for bf in self.bounded_funcs],
            [bf.func for bf in self.bounded_funcs],
        )


class ParametrisableFormFunc:
    """
    A class representing a parametrisable form function.

    This class is used to create a parametrized form function by setting
    reference points and generating bounded functions for inner segments.
    """

    def __init__(self, former: SegmentBuilder) -> None:
        """
        Initializes the ParametrisableFormFunc object with the given former
        segment builder.

        Args:
            former (SegmentBuilder): The former segment builder.
        """

        self._y = np.zeros(0)
        self._x = np.zeros(0)
        self._former = former

    def set_ref_points(
        self,
        x: npt.NDArray[np.float64],
        y: npt.NDArray[np.float64],
    ) -> None:
        """
        Sets the reference points for the ParametrisableFormFunc object.

        Args:
            x (npt.NDArray[np.float64]): An array of x dimension of
                reference points.
            y (npt.NDArray[np.float64]): An array of y dimension of
                reference points.

        Raises:
            ValueError: If the first reference point is not 0 or the length of
                reference points does not match the length of y.
            ValueError: If the first and last y are not both 0.

        """

        if not (y[[0, -1]] == np.array([0, 0])).all():
            raise ValueError("First and last frequency must be 0")
        if not x[0] == 0:
            raise ValueError("First reference point must be 0")
        if len(x) != len(y):
            raise ValueError("Length of x must match length of y")
        self._x = x
        self._y = y

    def get_parametrized(self) -> ParamizedFormFunc:
        """
        Generates a parametrized form function based on the reference points and inner segments.

        Returns:
            ParamizedFormFunc: A parametrized form function.

        """
        # We will store the bounded functions of the inner segments here
        inner_bounded_funcs = []

        # We copy the first and last x and y. This is helpful
        # for the following loop, but does not affect the result, since then
        # dx = x[i+1] - x[i] is always 0 for the first and
        # last field.
        x = [self._x[0], *self._x, self._x[-1]]
        y = [self._y[0], *self._y, self._y[-1]]

        for i in range(1, len(y) - 1):
            y0, y1 = y[i - 1], y[i]
            x0, x1 = x[i], x[i + 1]
            former_result = self._former(y0, y1, x0, x1)
            inner_bounded_funcs.extend(former_result)

        return ParamizedFormFunc(
            [
                BoundedFunction(-np.Inf, self._x[0], lambda _: np.array(0)),
                *inner_bounded_funcs,
                BoundedFunction(self._x[-1], np.Inf, lambda _: np.array(0)),
            ]
        )


def sanbox() -> None:
    ref_point_freqs = np.array([0, 3000, 2000, 0, 0])
    ref_points_times = np.array([0, 20, 40, 60, 80])

    samples = np.linspace(0, 100, 1000)

    pff = ParametrisableFormFunc(
        BendedSegmentBuilder(ramp_down_slope=-200, ramp_up_slope=500)
    )

    pff.set_ref_points(ref_points_times, ref_point_freqs)
    result = pff.get_parametrized()(samples)
    plt.plot(samples, result)

    ref_points_times = np.array([0, 21, 39, 62, 80])
    pff.set_ref_points(ref_points_times, ref_point_freqs)
    result = pff.get_parametrized()(samples)
    plt.plot(samples, result)

    ref_point_freqs = np.array([0, 2980, 2100, 0, 0])
    pff.set_ref_points(ref_points_times, ref_point_freqs)
    result = pff.get_parametrized()(samples)
    plt.plot(samples, result)

    plt.show()


if __name__ == "__main__":
    sanbox()
