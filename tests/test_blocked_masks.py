import numpy as np
import pytest
from floodlens.simulation import step

def test_binary_list_and_integer_masks_match_boolean_masks():
 z=np.zeros((8,8));h=np.full_like(z,.1);mask=np.zeros_like(z,dtype=bool);mask[3,4]=True
 expected,budget=step(z,h,.00001,blocked=mask)
 for supplied in [mask.astype(int),mask.tolist()]:
  actual,actual_budget=step(z,h,.00001,blocked=supplied)
  assert np.array_equal(actual,expected);assert actual_budget==budget
  assert actual[3,4]==h[3,4]
@pytest.mark.parametrize('value',[2,-1,np.nan])
def test_nonbinary_masks_rejected(value):
 with pytest.raises(ValueError):step(np.zeros((8,8)),np.zeros((8,8)),0,blocked=np.full((8,8),value))
