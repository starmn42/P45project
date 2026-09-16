from p45_reproductions.crowd_retail_exp001_calibration import (
    exact_subset_probabilities, exact_subset_sample, validate_sampler,
)
import numpy as np


def test_exact_sampler_validation():
    assert validate_sampler()["status"] == "PASS"


def test_exact_probabilities_normalize():
    probabilities = exact_subset_probabilities([0.3, 0.8, 2.0, 4.0], 2)
    assert abs(sum(probabilities.values()) - 1.0) < 1e-15


def test_exact_sampler_selects_exact_count():
    rng = np.random.default_rng(7)
    assert len(exact_subset_sample([0.3, 0.8, 2.0, 4.0], 2, rng)) == 2
