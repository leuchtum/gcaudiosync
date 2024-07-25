from typing import Any, overload

import numpy as np
import numpy.typing as npt


@overload
def convert_to_idx(
    x: npt.NDArray[Any],
    x_max: float,
    n_x: int,
) -> npt.NDArray[np.int64]: ...


@overload
def convert_to_idx(
    x: float,
    x_max: float,
    n_x: int,
) -> int: ...


def convert_to_idx(
    x: npt.NDArray[Any] | float,
    x_max: float,
    n_x: int,
) -> npt.NDArray[np.int64] | int:
    idx = x // (x_max / n_x)
    if isinstance(idx, float):
        return int(idx)
    return idx.astype(np.int64)
