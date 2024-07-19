from dataclasses import dataclass
from typing import Callable, Protocol

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt


@dataclass
class BoundedFunction:
    start: float
    end: float
    func: Callable[[npt.NDArray[np.float64]], npt.NDArray[np.float64]]

    def condition(self, time: npt.NDArray[np.float64]) -> npt.NDArray[np.bool_]:
        return (time >= self.start) & (time < self.end)


class SegmentBuilder(Protocol):
    def __call__(
        self, freq0: float, freq1: float, t0: float, t1: float
    ) -> list[BoundedFunction]: ...


@dataclass
class LinearSegmentBuilder:
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
    def __call__(
        self, _: float, freq1: float, t0: float, t1: float
    ) -> list[BoundedFunction]:
        duration = t1 - t0
        if duration == 0:
            return []
        return [BoundedFunction(t0, t1, lambda _: np.array(freq1))]


@dataclass
class BendedSegmentBuilder:
    unsigned_slope: float

    def __call__(
        self, freq0: float, freq1: float, t0: float, t1: float
    ) -> list[BoundedFunction]:
        duration = t1 - t0
        if duration == 0:
            return []

        # Determine the slope of the linear part
        slope_signed = np.sign(freq1 - freq0) * self.unsigned_slope

        # np.sign == 0 means that freq1 == freq0, thus no bend is needed
        if slope_signed == 0:
            return [*PleateauSegmentBuilder()(freq0, freq1, t0, t1)]

        # From here on the slope is non-zero, thus a bend is needed
        t_middle = t0 + (freq1 - freq0) / slope_signed
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

    Methods:
        __call__(time: npt.ArrayLike) -> npt.ArrayLike: Evaluates the bounded functions based on the given time parameter.
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
    def __init__(self, freqs: npt.NDArray[np.float64], former: SegmentBuilder) -> None:
        if not (freqs[[0, -1]] == np.array([0, 0])).all():
            raise ValueError("First and last frequency must be 0")
        self._freqs = freqs
        self._params = np.zeros_like(freqs)
        self._former = former

    def set_params(self, params: npt.NDArray[np.float64]) -> None:
        if not (params[0] == 0 and params[-1] == np.Inf):
            raise ValueError("First and last parameter must be 0 and np.Inf")
        if len(params) != len(self._freqs):
            raise ValueError("Length of params must match length of freqs")
        self._params = params

    def produce(self) -> ParamizedFormFunc:
        # We will store the bounded functions of the inner segments here
        inner_bounded_funcs = []

        # We copy the first and last frequency and parameter. This is helpful
        # for the following loop, but does not affect the result, since
        # duration = parameter[i+1] - parameter[i] is always 0 for the first and
        # last field.
        freqs = [self._freqs[0], *self._freqs, self._freqs[-1]]
        params = [self._params[0], *self._params, self._params[-1]]

        for i in range(1, len(freqs) - 1):
            freq0, freq1 = freqs[i - 1], freqs[i]
            t0, t1 = params[i], params[i + 1]
            former_result = self._former(freq0, freq1, t0, t1)
            inner_bounded_funcs.extend(former_result)

        return ParamizedFormFunc(
            [
                BoundedFunction(-np.Inf, self._params[0], lambda _: np.array(0)),
                *inner_bounded_funcs,
                BoundedFunction(self._params[-1], np.Inf, lambda _: np.array(0)),
            ]
        )


freqs = np.array([0, 3000, 2000, 0, 0])
x = np.linspace(0, 100, 1000)

pff = ParametrisableFormFunc(freqs, BendedSegmentBuilder(400))


ref_points = np.array([0, 20, 40, 60, np.Inf])
pff.set_params(ref_points)
y = pff.produce()(x)
plt.plot(x, y)

ref_points = np.array([0, 21, 39, 62, np.Inf])
pff.set_params(ref_points)
y = pff.produce()(x)
plt.plot(x, y)

pass
