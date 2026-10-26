from pathlib import Path
import numpy as np
import pytest
from fastapi.testclient import TestClient
from floodlens.simulation import Config,terrain,simulate,step
from floodlens.policy import gauges,observations,features,route,inspection_events,assimilate
from floodlens.model import fit,predict,load
from floodlens.api import app

def test_dry_and_seed_replay():
    a=simulate(Config(intensity=0));assert not np.any(a['depth'])
    a=simulate(Config());b=simulate(Config());assert np.array_equal(a['depth'],b['depth']);assert a['depth'].min()>=0

def test_conservation_and_impermeable():
    z=np.zeros((8,8));h=np.zeros_like(z);h[3,3]=1;blocked=np.zeros_like(z,dtype=bool);blocked[3,4]=True
    out,b=step(z,h,.00001,blocked=blocked);assert out[3,4]==0;assert abs(b['residual_m3'])<1e-10;assert out.min()>=0

def test_head_slope_direction_and_flat_equilibrium():
    z=np.zeros((8,8));h=np.zeros_like(z);h[3,3]=.1
    out,_=step(z,h,0,drain_rate=0);assert out[3,2]>0 and out[3,3]<.1
    h=np.full((8,8),.1);out,_=step(z,h,0,drain_rate=0);assert np.allclose(out[1:-2],h[1:-2])

def test_time_convergence_fixed_duration():
    z=np.zeros((8,8));base=np.zeros_like(z);base[3,3]=.1
    def evolve(dt):
        h=base.copy()
        for _ in range(int(200/dt)):h,_=step(z,h,0,dt,drain_rate=0)
        return h
    coarse=evolve(20);medium=evolve(10);fine=evolve(5)
    assert np.linalg.norm(medium-fine)<np.linalg.norm(coarse-medium)

def test_causal_features_invariant_to_future_mutation():
    run=simulate(Config());sites=gauges(run['z']);obs=observations(run,sites,33)
    x=features(run,sites,obs,10,(8,8));run['depth'][11:]=99;run['rain'][11:]=999;obs[11:]=77
    assert np.array_equal(x,features(run,sites,obs,10,(8,8)))

def test_route_and_placement_constraints():
    z,_=terrain(Config());assert len(set(gauges(z)))==3
    r=route(z,np.arange(6));assert r['distance_m']<=r['budget_m'];assert r['duration_s']<=r['time_budget_s'];assert all(a['arrival_s']>0 for a in r['arrivals']);assert np.all(np.diff([a['arrival_s'] for a in r['arrivals']])>0)
    assert not route(z,np.arange(6),time_budget_s=1)['arrivals']

def test_fit_and_schema_and_heldout():
    rng=np.random.default_rng(3);X=rng.normal(size=(100,8));y=.5+.2*X[:,0];m=fit(X,y);assert np.mean(abs(predict(m,X)-np.maximum(0,y)))<.01
    m=load(Path('models/nowcast.json'));sets=[set(m[k]) for k in ['train_families','validation_families','test_families']];assert not sets[0]&sets[1] and not sets[0]&sets[2] and not sets[1]&sets[2]

def test_api_integration_and_validation():
    c=TestClient(app);assert c.get('/api/health').json()['synthetic']
    r=c.post('/api/scenario',json={});assert r.status_code==200;d=r.json();assert len(d['depth'])==90;assert len(d['predictions'][0])==6
    assert c.post('/api/scenario',json={'intensity':999}).status_code==422;assert c.post('/api/scenario',json={'policy':'bad'}).status_code==422;assert c.get('/api/metrics').status_code==200

def test_invalid_config():
    with pytest.raises(ValueError):simulate(Config(steps=100000))

def test_site_time_noise_pairs_identical():
    run=simulate(Config());a=observations(run,[(4,7),(6,9)],33);b=observations(run,[(6,9)],33);assert np.array_equal(a[:,1],b[:,0])

def test_inspection_arrival_causality_and_update():
    run=simulate(Config());plan=route(run['z'],np.arange(6));ev=inspection_events(run,plan,22,start_s=300)
    p=np.zeros((90,6));a=assimilate(p,ev);first=min(e['available_step'] for e in ev);assert np.array_equal(a[:first],p[:first]);assert not np.array_equal(a,p)
    changed=[dict(e,depth_m=e['depth_m']+.1) for e in ev];b=assimilate(p,changed);assert np.array_equal(a[:first],b[:first])
    assert all(e['available_step']*20>=e['arrival_s'] for e in ev)

def test_api_model_missing_fallback(tmp_path,monkeypatch):
    import floodlens.api as api
    monkeypatch.setattr(api,'ROOT',tmp_path)
    d=TestClient(app).post('/api/scenario',json={}).json()
    assert d['model']=='interpolation fallback' and d['interval90_m'] is None
