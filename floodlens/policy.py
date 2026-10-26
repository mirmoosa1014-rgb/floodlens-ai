"""Policies use fixed terrain and noisy history; no hidden future field access."""
import numpy as np
from .simulation import crossings

def gauges(z,kind='information',seed=0,budget=3):
    n=len(z);sites=crossings(n)
    if kind=='random':ids=np.random.default_rng(seed).choice(len(sites),budget,replace=False)
    elif kind=='grid':ids=np.linspace(0,len(sites)-1,budget,dtype=int)
    else:
        ids=[]
        for _ in range(budget):
            scores=[(float(np.std(z[max(0,r-2):r+3,max(0,c-2):c+3]))+.002)*(1+min([np.hypot(r-sites[j][0],c-sites[j][1]) for j in ids] or [n])) if i not in ids else -1 for i,(r,c) in enumerate(sites)]
            ids.append(int(np.argmax(scores)))
    return [sites[i] for i in ids]

def measurement_noise(seed,t,r,c):
    # Same physical site/time receives identical exogenous noise across policies.
    return float(np.random.default_rng(np.random.SeedSequence([int(seed),int(t),int(r),int(c)])).normal(0,.0015))

def observations(run,sites,seed):
    return np.maximum(0,np.array([[h[r,c]+measurement_noise(seed,t,r,c) for r,c in sites] for t,h in enumerate(run['depth'])]))

def features(run,sites,obs,t,target):
    r,c=target;dist=np.array([np.hypot(r-a,c-b) for a,b in sites]);w=1/(1+dist)**2;w/=w.sum()
    now=float(obs[t]@w);old=float(obs[max(0,t-3)]@w);z=run['z'];elev=float(z[r,c]);gauge_elev=float(np.array([z[a,b] for a,b in sites])@w)
    return np.array([now,now-old,float(run['rain'][t])/100,float(np.mean(run['rain'][max(0,t-6):t+1]))/100,elev,gauge_elev,float(dist.min())/len(z),now*float(run['rain'][t])/100])

def route(z,estimate,budget_m=420,speed_m_s=6,time_budget_s=120,dwell_s=5,kind='priority'):
    if budget_m<0 or speed_m_s<=0 or time_budget_s<0 or dwell_s<0:raise ValueError('Invalid route budget')
    sites=crossings(len(z));base=(0,0);pos=base;elapsed=0.;distance=0.;arrivals=[];remaining=set(range(len(sites)))
    while remaining:
        feasible=[]
        for i in remaining:
            leg=float(np.linalg.norm(np.array(pos)-sites[i])*12);home=float(np.linalg.norm(np.array(base)-sites[i])*12)
            if distance+leg+home<=budget_m and elapsed+leg/speed_m_s+dwell_s+home/speed_m_s<=time_budget_s:
                score=(float(estimate[i])+.002)/(leg+12) if kind=='priority' else 1/(leg+12)
                feasible.append((score,i,leg))
        if not feasible:break
        _,i,leg=max(feasible);distance+=leg;elapsed+=leg/speed_m_s+dwell_s;arrivals.append(dict(crossing=i,arrival_s=elapsed));pos=sites[i];remaining.remove(i)
    home=float(np.linalg.norm(np.array(pos)-base)*12);distance+=home;elapsed+=home/speed_m_s
    return dict(arrivals=arrivals,distance_m=distance,budget_m=budget_m,duration_s=elapsed,time_budget_s=time_budget_s,dwell_s=dwell_s,missed=sorted(remaining),kind=kind)

def inspection_events(run,plan,seed,start_s=0):
    """Observation acquisition is stamped after travel+dwell, never before arrival."""
    sites=crossings(len(run['z']));events=[]
    for item in plan['arrivals']:
        arrival=start_s+item['arrival_s'];t=int(np.ceil(arrival/run['dt']))
        if t>=len(run['depth']):continue
        r,c=sites[item['crossing']]
        value=max(0,float(run['depth'][t,r,c])+measurement_noise(seed,t,r,c))
        events.append(dict(crossing=item['crossing'],arrival_s=arrival,available_step=t,depth_m=value))
    return events

def assimilate(predictions,events,dt=20):
    """Update only the observed crossing, persisting latest depth plus causal model change.

    No pre-arrival updates; expire point data after 180 s to avoid stale certainty.
    """
    pred=np.asarray(predictions);out=pred.copy()
    for t in range(len(pred)):
        for e in events:
            a=e['available_step'];c=e['crossing']
            if a<=t and (t-a)*dt<=180:
                # At arrival, the baseline horizon increment uses only issued forecasts.
                horizon_delta=pred[t,c]-pred[max(0,t-3),c]
                out[t,c]=max(0,e['depth_m']+horizon_delta)
    return out
