import json
import pytest
from floodlens.model import load,FEATURES
@pytest.mark.parametrize('key,value',[('scale',[0]*8),('scale',[-1]*8),('mean',[0]),('weights',[float('nan')]*9),('mean',[float('inf')]*8)])
def test_model_numeric_schema(tmp_path,key,value):
 m=dict(feature_schema=FEATURES,mean=[0]*8,scale=[1]*8,weights=[0]*9);m[key]=value
 p=tmp_path/'model.json';p.write_text(json.dumps(m))
 with pytest.raises(ValueError):load(p)
