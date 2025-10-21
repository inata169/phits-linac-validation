import os
import sys

import pytest


def _require_runtime_deps():
    pytest.importorskip("numpy")
    pytest.importorskip("pandas")
    pytest.importorskip("matplotlib")
    pytest.importorskip("scipy")
    pytest.importorskip("pymedphys")


def _import_module():
    _require_runtime_deps()
    sys.path.insert(0, os.path.abspath("src"))
    import ocr_true_scaling as mod  # type: ignore
    return mod


def test_load_csv_profile_normalises_max_to_one():
    mod = _import_module()
    path = os.path.join("test", "measured_csv", "05x05m05cm-xXlat.csv")
    x, y = mod.load_csv_profile(path)
    assert len(x) > 10 and len(y) == len(x)
    assert abs(float(y.max()) - 1.0) < 1e-6


def test_parse_phits_out_profile_returns_normalised_series():
    mod = _import_module()
    path = os.path.join("test", "PHITS", "deposit-y-water-100x.out")
    axis, x, y, meta = mod.parse_phits_out_profile(path)
    assert isinstance(axis, str)
    assert len(x) > 0 and len(y) == len(x)
    assert abs(float(y.max()) - 1.0) < 1e-6
    assert isinstance(meta, dict)


def test_center_normalise_aligns_origin_and_scales_center_to_one():
    mod = _import_module()
    import numpy as np

    x = np.array([-0.1, 0.0, 0.1], float)
    y = np.array([0.5, 1.0, 0.5], float)
    xx, yy = mod.center_normalise(x, y, tol_cm=0.05, interp=False)
    # Origin shift
    assert abs(float(xx[np.argmin(abs(xx))])) < 1e-12
    # Center scaling
    assert abs(float(yy[np.argmin(abs(xx))]) - 1.0) < 1e-12

