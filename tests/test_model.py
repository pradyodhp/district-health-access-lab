import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from health_access.model import Assumption, compare, evaluate, funnel
from health_access.scenarios import training_scenario, training_outreach
from health_access.simulation import simulate


def test_conservation_and_known_answer():
    result = funnel(1000, .2, .5, .5, .5, 100, 10000)
    assert [result[k] for k in ("eligible", "need_proxy", "aware", "screened", "followed_up")] == [1000, 200, 100, 50, 25]
    assert result["unscreened_need_proxy"] == 150


def test_more_uptake_cannot_reduce_screened_and_capacity_caps():
    first = funnel(1000, .5, .5, .2, .5, 100, 0)
    more = funnel(1000, .5, .5, .8, .5, 100, 0)
    assert first["screened"] <= more["screened"] == 100


def test_invalid_and_unlabeled_inputs_rejected():
    with pytest.raises(ValueError):
        Assumption(.2, .3, 1.2, "rate", "sample")
    with pytest.raises(ValueError):
        Assumption(.2, .3, .5, "rate", "")
    with pytest.raises(ValueError):
        funnel(100, .2, 1.1, .5, .5, 100, 0)


def test_uncertainty_reproducible_and_ordered():
    one = simulate(training_scenario(), draws=300, seed=13)
    two = simulate(training_scenario(), draws=300, seed=13)
    assert one == two
    for band in one.values():
        assert band["p10"] <= band["p50"] <= band["p90"]


def test_training_comparison_requires_incremental_reach():
    result = compare(evaluate(training_scenario()), evaluate(training_outreach()))
    assert result["incremental_screened"] >= 0
    assert compare({"screened": 10, "spend_inr": 100}, {"screened": 10, "spend_inr": 200})["inr_per_extra_screened"] is None
