from typing import Callable

import numpy as np
import numpy.typing as npt
import tqdm

from gcaudiosync.audioanalyser.mask import MaskFactory
from gcaudiosync.audioanalyser.piecewise import ParametrisableFormFunc
from gcaudiosync.audioanalyser.slicer import Slicer, SlicerFactory, ValueSlicerConfig


class RefPointOptimizer:
    """Class for optimizing reference points."""

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
        """
        Initializes the Optimize object.
        Parameters:
        - param_form_func: The parametrisable form function.
        - mask_factory: The mask factory.
        - slicer_factory: The slicer factory.
        - x_sample: The x sample.
        - S: The S array.
        - dx: The dx value.
        - dy: The dy value.
        - use_1st_harmonic: Whether to use the 1st harmonic. Default is True.
        - callback: The callback function. Default is None.
        """

        self.param_form_func = param_form_func
        self.x_sample = x_sample
        self.mask_fac = mask_factory
        self.slicer_fac = slicer_factory
        self.S = S
        self.dx = dx
        self.dy = dy
        self.use_1st_harmonic = use_1st_harmonic
        self.callback = callback

    def _build_mask(
        self, x: npt.NDArray[np.float64], y: npt.NDArray[np.float64], slicer: Slicer
    ) -> npt.NDArray[np.bool_]:
        "Helper function to build a mask."
        self.param_form_func.set_ref_points(x, y)
        form = self.param_form_func.get_parametrized()(self.x_sample[slicer.x_slice])
        mask_freq = self.mask_fac.build_binary_mask(form, slicer)
        if not self.use_1st_harmonic:
            return mask_freq
        mask_1st_harmonic = self.mask_fac.build_binary_mask(2 * form, slicer)
        return mask_freq | mask_1st_harmonic

    def _determine_score(
        self,
        x: npt.NDArray[np.float64],
        y: npt.NDArray[np.float64],
        S_reduced: npt.NDArray[np.float32],
        slicer: Slicer,
    ) -> float:
        "Helper function to determine the score."
        mask = self._build_mask(x, y, slicer)
        if self.callback is not None:
            self.callback(slicer, mask)
        return S_reduced[mask].sum()  # type: ignore

    def _optimize(
        self,
        *,
        x_proposed: npt.NDArray[np.float64],
        y_proposed: npt.NDArray[np.float64],
        n: int,
        slicer: Slicer,
    ) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
        "Helper function to optimize."
        scores = np.empty(n, dtype=np.float64)
        S_reduced = self.S[slicer.matrix_slice]
        for i in tqdm.tqdm(range(n)):
            scores[i] = self._determine_score(
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
        """Optimize the reference point in x direction at the given index."""
        n = int((xi_ub - xi_lb) / self.dx * resolution)

        x_proposed = np.tile(x, (n, 1))
        x_proposed[:, xi_idx] = np.linspace(xi_lb, xi_ub, n)
        y_proposed = np.tile(y, (n, 1))

        slicer = self.slicer_fac.build(ValueSlicerConfig(from_x=xi_lb, to_x=xi_ub))

        return self._optimize(
            x_proposed=x_proposed,
            y_proposed=y_proposed,
            n=n,
            slicer=slicer,
        )

    def optimize_yi(
        self,
        x: npt.NDArray[np.float64],
        y: npt.NDArray[np.float64],
        yi_idx: int,
        yi_lb: float,
        yi_ub: float,
        resolution: int,
    ) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
        """Optimize the reference point in y direction at the given index."""
        n = int((yi_ub - yi_lb) / self.dy * resolution)

        x_proposed = np.tile(x, (n, 1))
        y_proposed = np.tile(y, (n, 1))
        y_proposed[:, yi_idx] = np.linspace(yi_lb, yi_ub, n)

        slicer = self.slicer_fac.build(ValueSlicerConfig(from_y=yi_lb, to_y=yi_ub))

        return self._optimize(
            x_proposed=x_proposed,
            y_proposed=y_proposed,
            n=n,
            slicer=slicer,
        )

    def optimize_all_x(
        self,
        x: npt.NDArray[np.float64],
        y: npt.NDArray[np.float64],
        resolution: float,
    ) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
        """Optimize the reference points in x direction."""
        diff_last_elements = x[-1] - x[-2]

        n = int(diff_last_elements / self.dx * resolution)

        x_proposed = np.linspace(x, x + diff_last_elements, n)
        x_proposed[:, 0] = x[0]
        x_proposed[:, -1] = x[-1]

        y_proposed = np.tile(y, (n, 1))

        slicer = self.slicer_fac.build()

        return self._optimize(
            x_proposed=x_proposed,
            y_proposed=y_proposed,
            n=n,
            slicer=slicer,
        )
