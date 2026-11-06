import numpy as np
import pytest
from floodlens.policy import gauges


@pytest.mark.parametrize('policy',['random','grid','information'])
@pytest.mark.parametrize('budget',[7,-1,1.5,True])
def test_invalid_gauge_budget_rejected(policy,budget):
    with pytest.raises(ValueError):gauges(np.zeros((16,16)),policy,budget=budget)


def test_unknown_gauge_policy_rejected():
    with pytest.raises(ValueError):gauges(np.zeros((16,16)),'informaton')


@pytest.mark.parametrize('policy',['random','grid','information'])
def test_full_gauge_budget_is_unique(policy):
    assert len(set(gauges(np.zeros((16,16)),policy,budget=6)))==6
    assert gauges(np.zeros((16,16)),policy,budget=0)==[]
