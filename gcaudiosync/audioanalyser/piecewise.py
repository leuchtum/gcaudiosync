from dataclasses import dataclass
from typing import Callable, Protocol

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt


@dataclass
class BoundedFunction:
    """
    Represents a bounded function with a start and end time.

    Attributes:
        start (float): The start time of the bounded function.
        end (float): The end time of the bounded function.
        func (Callable[[npt.NDArray[np.float64]], npt.NDArray[np.float64]]): The function to be applied within the bounds.
    """

    start: float
    end: float
    func: Callable[[npt.NDArray[np.float64]], npt.NDArray[np.float64]]

    def condition(self, time: npt.NDArray[np.float64]) -> npt.NDArray[np.bool_]:
        """
        Check if each element in the input time array falls within the bounds of the function.

        Args:
            time (npt.NDArray[np.float64]): The array of time values to check.

        Returns:
            npt.NDArray[np.bool_]: A boolean array indicating whether each element in the input time array falls within the bounds of the function.
        """
        return (time >= self.start) & (time < self.end)


class SegmentBuilder(Protocol):
    """
    A protocol for building segments of bounded functions.
    """

    def __call__(
        self, freq0: float, freq1: float, t0: float, t1: float
    ) -> list[BoundedFunction]:
        """
        Build a segment of bounded functions.

        Parameters:
        - freq0 (float): The starting frequency of the segment.
        - freq1 (float): The ending frequency of the segment.
        - t0 (float): The starting time of the segment.
        - t1 (float): The ending time of the segment.

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
        self, freq0: float, freq1: float, t0: float, t1: float
    ) -> list[BoundedFunction]:
        duration = t1 - t0
        if duration == 0:
            return []
        slope = (freq1 - freq0) / duration
        return [BoundedFunction(t0, t1, lambda t: freq0 + slope * (t - t0))]


@dataclass
class PleateauSegmentBuilder:
    """
    A class that builds plateau segments of bounded functions.
    """

    def __call__(
        self, _: float, freq1: float, t0: float, t1: float
    ) -> list[BoundedFunction]:
        duration = t1 - t0
        if duration == 0:
            return []
        return [BoundedFunction(t0, t1, lambda _: np.array(freq1))]


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
        self, freq0: float, freq1: float, t0: float, t1: float
    ) -> list[BoundedFunction]:
        duration = t1 - t0
        if duration == 0:
            return []

        # Determine the slope of the linear part
        slope = self.ramp_up_slope if freq1 > freq0 else self.ramp_down_slope

        # np.sign == 0 means that freq1 == freq0, thus no bend is needed
        if slope == 0:
            return [*PleateauSegmentBuilder()(freq0, freq1, t0, t1)]

        # From here on the slope is non-zero, thus a bend is needed
        t_middle = t0 + (freq1 - freq0) / slope
        return [
            *LinearSegmentBuilder()(freq0, freq1, t0, t_middle),
            *PleateauSegmentBuilder()(freq1, freq1, t_middle, t1),
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

    def __call__(self, time: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
        """
        Evaluates the bounded functions based on the given time parameter.

        Args:
            time (npt.ArrayLike): The time parameter for evaluation.

        Returns:
            npt.ArrayLike: The evaluated result based on the bounded functions.

        """
        return np.piecewise(
            time,
            [bf.condition(time) for bf in self.bounded_funcs],
            [bf.func for bf in self.bounded_funcs],
        )


class ParametrisableFormFunc:
    """
    A class representing a parametrisable form function.

    This class is used to create a parametrized form function by setting
    reference points and generating bounded functions for inner segments.
    """

    def __init__(self, freqs: npt.NDArray[np.float64], former: SegmentBuilder) -> None:
        """
        Initializes the ParametrisableFormFunc object with the given frequencies
        and former segment builder.

        Args:
            freqs (numpy.ndarray): An array of frequencies.
            former (SegmentBuilder): The former segment builder.

        Raises:
            ValueError: If the first and last frequency are not both 0.
        """

        if not (freqs[[0, -1]] == np.array([0, 0])).all():
            raise ValueError("First and last frequency must be 0")
        self._freqs = freqs
        self._ref_points = np.zeros_like(freqs)
        self._former = former

    def set_ref_points(self, ref_points: npt.NDArray[np.float64]) -> None:
        """
        Sets the reference points for the ParametrisableFormFunc object.

        Args:
            ref_points (npt.NDArray[np.float64]): An array of reference points.

        Raises:
            ValueError: If the first reference point is not 0 or the length of reference points does not match the length of freqs.

        """
        if not ref_points[0] == 0:
            raise ValueError("First reference point must be 0")
        if len(ref_points) != len(self._freqs):
            raise ValueError("Length of reference points must match length of freqs")
        self._ref_points = ref_points

    def get_parametrized(self) -> ParamizedFormFunc:
        """
        Generates a parametrized form function based on the reference points and inner segments.

        Returns:
            ParamizedFormFunc: A parametrized form function.

        """
        # We will store the bounded functions of the inner segments here
        inner_bounded_funcs = []

        # We copy the first and last frequency and ref point. This is helpful
        # for the following loop, but does not affect the result, since then
        # duration = ref_point[i+1] - ref_point[i] is always 0 for the first and
        # last field.
        freqs = [self._freqs[0], *self._freqs, self._freqs[-1]]
        ref_points = [self._ref_points[0], *self._ref_points, self._ref_points[-1]]

        for i in range(1, len(freqs) - 1):
            freq0, freq1 = freqs[i - 1], freqs[i]
            p0, p1 = ref_points[i], ref_points[i + 1]
            former_result = self._former(freq0, freq1, p0, p1)
            inner_bounded_funcs.extend(former_result)

        return ParamizedFormFunc(
            [
                BoundedFunction(-np.Inf, self._ref_points[0], lambda _: np.array(0)),
                *inner_bounded_funcs,
                BoundedFunction(self._ref_points[-1], np.Inf, lambda _: np.array(0)),
            ]
        )


def sanbox() -> None:
    freqs = np.array([0, 3000, 2000, 0, 0])
    x = np.linspace(0, 100, 1000)

    pff = ParametrisableFormFunc(
        freqs, BendedSegmentBuilder(ramp_down_slope=-200, ramp_up_slope=500)
    )

    ref_points = np.array([0, 20, 40, 60, 80])
    pff.set_ref_points(ref_points)
    y = pff.get_parametrized()(x)
    plt.plot(x, y)

    ref_points = np.array([0, 21, 39, 62, 80])
    pff.set_ref_points(ref_points)
    y = pff.get_parametrized()(x)
    plt.plot(x, y)
    plt.show()


if __name__ == "__main__":
    sanbox()
