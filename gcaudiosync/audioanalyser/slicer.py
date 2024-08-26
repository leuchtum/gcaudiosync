from dataclasses import dataclass
from typing import TypeVar

import numpy as np
import numpy.typing as npt

from gcaudiosync.audioanalyser.util import convert_to_idx

_E = TypeVar("_E", bound=np.generic, covariant=True)


class _SlicerConfig:
    "Main class for the slicer configuration."

    from_x: float | int | None = None
    to_x: float | int | None = None
    from_y: float | int | None = None
    to_y: float | int | None = None

    def __post_init__(self) -> None:
        # Some checks to ensure the configuration is valid.
        if self.from_x is not None and self.to_x is not None:
            if self.from_x >= self.to_x:
                raise ValueError("from_x must be smaller than to_x")
        if self.from_y is not None and self.to_y is not None:
            if self.from_y >= self.to_y:
                raise ValueError("from_y must be smaller than to_y")


@dataclass(kw_only=True, frozen=True)
class IndexSlicerConfig(_SlicerConfig):
    """Class for the index slicer configuration."""
    from_x: int | None = None
    to_x: int | None = None
    from_y: int | None = None
    to_y: int | None = None


@dataclass(kw_only=True, frozen=True)
class ValueSlicerConfig(_SlicerConfig):
    """Class for the value slicer configuration."""
    from_x: float | None = None
    to_x: float | None = None
    from_y: float | None = None
    to_y: float | None = None

    def convert_to_idx_config(
        self,
        n_x: int,
        n_y: int,
        x_max: float,
        y_max: float,
    ) -> IndexSlicerConfig:
        """ Convert the value slicer configuration to an index slicer configuration. """
        def convert_to_idx_if_not_none(
            z: float | None,
            z_max: float,
            n_z: int,
        ) -> int | None:
            if z is None:
                return None
            return convert_to_idx(z, z_max, n_z)

        return IndexSlicerConfig(
            from_x=convert_to_idx_if_not_none(self.from_x, x_max, n_x),
            to_x=convert_to_idx_if_not_none(self.to_x, x_max, n_x),
            from_y=convert_to_idx_if_not_none(self.from_y, y_max, n_y),
            to_y=convert_to_idx_if_not_none(self.to_y, y_max, n_y),
        )


@dataclass(frozen=True, kw_only=True)
class Slicer:
    """ Class for slicing a matrix, given the bounds of the matrix. """
    n_x: int
    n_y: int
    x_max: float
    y_max: float
    from_x: int
    to_x: int
    from_y: int
    to_y: int

    @property
    def x_slice(self) -> slice:
        return slice(self.from_x, self.to_x)

    @property
    def y_slice(self) -> slice:
        return slice(self.from_y, self.to_y)

    @property
    def matrix_slice(self) -> tuple[slice, slice]:
        return self.y_slice, self.x_slice

    def _handle_x(self, x: npt.NDArray[_E]) -> npt.NDArray[_E]:
        need_shape = (self.n_x,)
        if x.shape != need_shape:
            msg = f"x must be shape {need_shape}, got {x.shape}"
            raise ValueError(msg)
        return x[self.x_slice]

    def _handle_y(self, y: npt.NDArray[_E]) -> npt.NDArray[_E]:
        need_shape = (self.n_y,)
        if y.shape != need_shape:
            msg = f"y must be shape {need_shape}, got {y.shape}"
            raise ValueError(msg)
        return y[self.y_slice]

    def _handle_matrix(self, matrix: npt.NDArray[_E]) -> npt.NDArray[_E]:
        need_shape = (self.n_y, self.n_x)
        if matrix.shape != need_shape:
            msg = f"matrix must be shape {need_shape}, got {matrix.shape}"
            raise ValueError(msg)
        return matrix[self.matrix_slice]

    def __call__(
        self,
        x: npt.NDArray[_E] | None = None,
        y: npt.NDArray[_E] | None = None,
        matrix: npt.NDArray[_E] | None = None,
    ) -> npt.NDArray[_E]:
        match (x is None, y is None, matrix is None):
            case (False, True, True):
                return self._handle_x(x)  # type: ignore[arg-type]
            case (True, False, True):
                return self._handle_y(y)  # type: ignore[arg-type]
            case (True, True, False):
                return self._handle_matrix(matrix)  # type: ignore[arg-type]
            case _:
                msg = "Exactly one of x, y or matrix must be given"
                raise ValueError(msg)


@dataclass(kw_only=True, frozen=True)
class SlicerFactory:
    """Class that builds matrix slicers from configurations."""
    n_x: int
    n_y: int
    x_max: float
    y_max: float
    global_slice_cfg: IndexSlicerConfig | ValueSlicerConfig | None = None

    def _parse_global_slice_cfg(self) -> IndexSlicerConfig:
        """Helper function to parse the global slice configuration."""
        if self.global_slice_cfg is None:
            return IndexSlicerConfig()
        if isinstance(self.global_slice_cfg, ValueSlicerConfig):
            return self.global_slice_cfg.convert_to_idx_config(
                self.n_x,
                self.n_y,
                self.x_max,
                self.y_max,
            )
        return self.global_slice_cfg

    def _parse_local_slice_cfg(
        self,
        local_slice_cfg: IndexSlicerConfig | ValueSlicerConfig | None,
    ) -> IndexSlicerConfig:
        """Helper function to parse the local slice configuration."""
        if local_slice_cfg is None:
            return IndexSlicerConfig()
        if isinstance(local_slice_cfg, ValueSlicerConfig):
            return local_slice_cfg.convert_to_idx_config(
                self.n_x,
                self.n_y,
                self.x_max,
                self.y_max,
            )
        return local_slice_cfg

    def build(
        self,
        local_slice_cfg: IndexSlicerConfig | ValueSlicerConfig | None = None,
    ) -> Slicer:
        """
        Build a slicer object for slicing a matrix. A local config can be
        given, it will be merged with the global config.
        """
        global_slice_cfg = self._parse_global_slice_cfg()
        local_slice_cfg = self._parse_local_slice_cfg(local_slice_cfg)
        from_x = max(
            global_slice_cfg.from_x or 0,
            local_slice_cfg.from_x or 0,
        )
        to_x = min(
            global_slice_cfg.to_x or self.n_x,
            local_slice_cfg.to_x or self.n_x,
        )
        from_y = max(
            global_slice_cfg.from_y or 0,
            local_slice_cfg.from_y or 0,
        )
        to_y = min(
            global_slice_cfg.to_y or self.n_y,
            local_slice_cfg.to_y or self.n_y,
        )
        return Slicer(
            n_x=self.n_x,
            n_y=self.n_y,
            x_max=self.x_max,
            y_max=self.y_max,
            from_x=from_x,
            to_x=to_x,
            from_y=from_y,
            to_y=to_y,
        )
