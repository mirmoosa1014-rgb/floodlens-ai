import numpy as np
from floodlens.policy import assimilate

def test_inspection_correction_advances_from_observation_epoch():
    pred=np.arange(16,dtype=float)[:,None]*.1
    event={'available_step':4,'crossing':0,'depth_m':.5}
    result=assimilate(pred,[event])
    assert np.array_equal(result[:4],pred[:4])
    # Forecasts lead truth by 3 steps: pred[1] is the issued forecast for arrival step 4.
    assert np.isclose(result[4,0],.5+pred[4,0]-pred[1,0])
    assert np.isclose(result[6,0],.5+pred[6,0]-pred[1,0])
    assert np.isclose(result[13,0],.5+pred[13,0]-pred[1,0])
    assert result[14,0]==pred[14,0]
