from pathlib import Path
import json
import numpy as np
from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel,Field
from .simulation import Config,simulate,crossings
from .policy import gauges,observations,features,route,inspection_events,assimilate
from .model import load,predict
ROOT=Path(__file__).resolve().parents[1]
app=FastAPI(title='FloodLens Synthetic Laboratory')
app.add_middleware(CORSMiddleware,allow_origins=['http://127.0.0.1:5103','http://localhost:5103'],allow_methods=['GET','POST'],allow_headers=['Content-Type'])
class Scenario(BaseModel):
    seed:int=Field(31,ge=0,le=100000)
    family:int=Field(7,ge=0,le=50)
    intensity:float=Field(65,ge=0,le=200)
    policy:str='information'
    threshold:float=Field(.015,gt=0,le=.2)
    route_policy:str='priority'
@app.get('/api/health')
def health():return {'status':'ok','synthetic':True}
@app.get('/api/metrics')
def metrics():return json.loads((ROOT/'results/summary.json').read_text())
@app.post('/api/scenario')
def scenario(s:Scenario):
    if s.policy not in ['random','grid','information'] or s.route_policy not in ['priority','nearest']:raise HTTPException(422,'Unknown policy')
    run=simulate(Config(seed=s.seed,family=s.family,intensity=s.intensity));sites=gauges(run['z'],s.policy,s.seed);obs=observations(run,sites,s.seed+1000)
    modelpath=ROOT/'models/nowcast.json';m=load(modelpath) if modelpath.exists() else None;predictions=[]
    for t in range(90):
        x=np.array([features(run,sites,obs,t,p) for p in crossings(16)]);q=predict(m,x) if m else x[:,0];predictions.append(q.tolist())
    # At t=15 (five minutes), use only then-issued forecasts to inspect likely issues.
    start=15;plan=route(run['z'],predictions[start],kind=s.route_policy);ev=inspection_events(run,plan,s.seed+2000,start_s=start*20);updated=assimilate(predictions,ev)
    return {'synthetic':True,'terrain':run['z'].tolist(),'blocked':run['blocked'].tolist(),'depth':run['depth'].tolist(),'rain':run['rain'].tolist(),'dt':20,'sites':sites,'observations':obs.tolist(),'predictions':updated.tolist(),'gauge_predictions':predictions,'crossings':crossings(16),'route':plan,'inspection_events':ev,'route_start_s':start*20,'interval90_m':m['interval90_m'] if m else None,'model':'ridge + causal inspection correction' if m else 'interpolation fallback','threshold':s.threshold,'max_mass_residual_m3':max(abs(b['residual_m3']) for b in run['budget'])}
if (ROOT/'frontend/dist').exists():app.mount('/',StaticFiles(directory=ROOT/'frontend/dist',html=True),name='frontend')
