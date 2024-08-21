from typing import Any, overload

import numpy as np
import numpy.typing as npt


def _handle_single_value(x: float | int, x_max: float, n_x: int, clip: bool) -> int:
    """Helper function to handle a single value."""
    idx = int(x // (x_max / n_x))
    if clip:
        idx = max(0, min(idx, n_x))
    return idx


def _handle_array(
    x: npt.NDArray[Any],
    x_max: float,
    n_x: int,
    clip: bool,
) -> npt.NDArray[np.int64]:
    """Helper function to handle an array or matrix."""
    idx = (x // (x_max / n_x)).astype(np.int64)
    if clip:
        idx = np.clip(idx, 0, n_x)
    return idx


@overload
def convert_to_idx(
    x: npt.NDArray[Any],
    x_max: float,
    n_x: int,
    clip: bool = True,
) -> npt.NDArray[np.int64]: ...


@overload
def convert_to_idx(
    x: float | int,
    x_max: float,
    n_x: int,
    clip: bool = True,
) -> int: ...


def convert_to_idx(
    x: npt.NDArray[Any] | float | int,
    x_max: float,
    n_x: int,
    clip: bool = True,
) -> npt.NDArray[np.int64] | int:
    """ Convert a value or array to an index."""
    if isinstance(x, float | int):
        return _handle_single_value(x, x_max, n_x, clip)
    return _handle_array(x, x_max, n_x, clip)
