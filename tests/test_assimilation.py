import numpy as np
from floodlens.policy import assimilate


def test_integer_forecasts_preserve_fractional_observation_depth():
    predictions = np.zeros((12, 6), dtype=int)
    result = assimilate(predictions, [{'available_step': 2, 'crossing': 0, 'depth_m': .125}])
    assert result[2, 0] == .125
    assert not predictions.any()


def test_latest_observation_wins_regardless_of_event_order():
    predictions = np.zeros((12, 6))
    early = {'available_step': 2, 'crossing': 0, 'depth_m': .1}
    later = {'available_step': 4, 'crossing': 0, 'depth_m': .2}
    forward = assimilate(predictions, [early, later])
    reverse = assimilate(predictions, [later, early])
    assert np.array_equal(forward, reverse)
    assert reverse[3, 0] == .1 and reverse[4, 0] == .2
