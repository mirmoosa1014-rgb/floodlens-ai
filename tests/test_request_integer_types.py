import pytest
from fastapi.testclient import TestClient
from floodlens.api import app

@pytest.mark.parametrize('field',['seed','family'])
@pytest.mark.parametrize('value',[True,False,3.0,'3'])
def test_integer_scenario_fields_reject_coercion(field,value):
    with TestClient(app) as client:
        assert client.post('/api/scenario',json={field:value}).status_code==422
