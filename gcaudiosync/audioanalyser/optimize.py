from typing import Callable

import numpy as np
import numpy.typing as npt
import tqdm

from gcaudiosync.audioanalyser.mask import MaskFactory
from gcaudiosync.audioanalyser.piecewise import ParametrisableFormFunc
from gcaudiosync.audioanalyser.slicer import Slicer, SlicerFactory, ValueSlicerConfig


class RefPointOptimizer:
    def __init__(
        self,
        *,
        param_form_func: ParametrisableFormFunc,
        mask_factory: MaskFactory,
        slicer_factory: SlicerFactory,
        x_sample: npt.NDArray[np.float64],
        S: npt.NDArray[np.float32],
        dx: float,
        dy: float,
        use_1st_harmonic: bool = True,
        callback: Callable[[Slicer, npt.NDArray[np.bool_]], None] | None = None,
    ) -> None:
        self.param_form_func = param_form_func
        self.x_sample = x_sample
        self.mask_fac = mask_factory
        self.slicer_fac = slicer_factory
        self.S = S
        self.dx = dx
        self.dy = dy
        self.use_1st_harmonic = use_1st_harmonic
        self.callback = callback

    def build_mask(
        self, x: npt.NDArray[np.float64], y: npt.NDArray[np.float64], slicer: Slicer
    ) -> npt.NDArray[np.bool_]:
        self.param_form_func.set_ref_points(x, y)
        form = self.param_form_func.get_parametrized()(self.x_sample[slicer.x_slice])
        mask_freq = self.mask_fac.build_binary_mask(form, slicer)
        if not self.use_1st_harmonic:
            return mask_freq
        mask_1st_harmonic = self.mask_fac.build_binary_mask(2 * form, slicer)
        return mask_freq | mask_1st_harmonic

    def determine_score(
        self,
        x: npt.NDArray[np.float64],
        y: npt.NDArray[np.float64],
        S_reduced: npt.NDArray[np.float32],
        slicer: Slicer,
    ) -> float:
        mask = self.build_mask(x, y, slicer)
        if self.callback is not None:
            self.callback(slicer, mask)
        return S_reduced[mask].sum() # type: ignore

    def optimize(
        self,
        x_proposed: npt.NDArray[np.float64],
        y_proposed: npt.NDArray[np.float64],
        n: int,
        slicer: Slicer,
    ) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
        scores = np.empty(n, dtype=np.float64)
        S_reduced = self.S[slicer.matrix_slice]
        for i in tqdm.tqdm(range(n)):
            scores[i] = self.determine_score(
                x_proposed[i, :],
                y_proposed[i, :],
                S_reduced,
                slicer,
            )
        return x_proposed[np.argmax(scores), :], y_proposed[np.argmax(scores), :]

    def optimize_xi(
        self,
        x: npt.NDArray[np.float64],
        y: npt.NDArray[np.float64],
        xi_idx: int,
        xi_lb: float,
        xi_ub: float,
        resolution: int,
    ) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
        x_lower = x.copy()
        x_upper = x.copy()

        x_lower[xi_idx] = xi_lb
        x_upper[xi_idx] = xi_ub

        n = int((xi_ub - xi_lb) / self.dx * resolution)
        x_proposed = np.linspace(x_lower, x_upper, n)
        y_proposed = np.tile(y, (n, 1))

        slicer = self.slicer_fac.build(ValueSlicerConfig(from_x=xi_lb, to_x=xi_ub))

        return self.optimize(x_proposed, y_proposed, n, slicer)

    def optimize_yi(
        self,
        x: npt.NDArray[np.float64],
        y: npt.NDArray[np.float64],
        yi_idx: int,
        yi_lb: float,
        yi_ub: float,
        resolution: int,
    ) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
        y_lower = y.copy()
        y_upper = y.copy()

        y_lower[yi_idx] = yi_lb
        y_upper[yi_idx] = yi_ub

        n = int((yi_ub - yi_lb) / self.dy * resolution)
        x_proposed = np.tile(x, (n, 1))
        y_proposed = np.linspace(y_lower, y_upper, n)

        slicer = self.slicer_fac.build(ValueSlicerConfig(from_y=yi_lb, to_y=yi_ub))

        return self.optimize(x_proposed, y_proposed, n, slicer)
