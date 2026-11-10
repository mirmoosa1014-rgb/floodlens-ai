import numpy as np
import pytest
from floodlens.model import fit
@pytest.mark.parametrize('X,y',[(np.empty((0,8)),np.empty(0)),(np.ones((3,7)),np.ones(3)),(np.ones((3,8)),np.ones((3,1))),(np.full((3,8),np.nan),np.ones(3))])
def test_invalid_training_data(X,y):
 with pytest.raises(ValueError):fit(X,y)
def test_list_input_supported():
 m=fit([[0]*8,[1]*8],[0,1]);assert len(m['weights'])==9
