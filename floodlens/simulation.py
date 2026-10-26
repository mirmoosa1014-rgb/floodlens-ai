"""Conservative, synthetic storage-cell hydrology. Lengths in metres, time in seconds."""
from dataclasses import dataclass
import numpy as np

@dataclass
class Config:
    seed: int = 31
    family: int = 7
    intensity: float = 65.0
    steps: int = 90
    n: int = 16
    dt: float = 20.0
    def validate(self):
        if not (0 <= self.seed <= 100000 and 0 <= self.family <= 50 and 0 <= self.intensity <= 200 and 10 <= self.steps <= 120 and 8 <= self.n <= 24 and 0 < self.dt <= 20):
            raise ValueError('Configuration outside bounded domain')

def terrain(cfg):
    cfg.validate();rng=np.random.default_rng(cfg.family)
    y,x=np.mgrid[:cfg.n,:cfg.n]
    z=.012*(cfg.n-y)+.010*abs(x-(cfg.n/2+1.4*np.sin(y/4)))+.006*np.sin(x/2+cfg.family)+rng.normal(0,.001,x.shape)
    blocked=np.zeros_like(z,dtype=bool);blocked[3:6,2]=True
    return z,blocked

def step(z,h,rain,dt=20,dx=12,blocked=None,drain_rate=1e-6):
    if dt<=0 or dt>20 or dx<=0 or rain<0: raise ValueError('Invalid step')
    blocked=np.zeros_like(h,dtype=bool) if blocked is None else blocked
    added=np.where(blocked,0,rain*dt);water=h+added
    drain=np.minimum(water,drain_rate*dt);drain[blocked]=0;water=water-drain
    head=z+water;outgoing=np.zeros_like(water);transfers=[]
    for axis in (0,1):
        a=[slice(None),slice(None)];b=a.copy();a[axis]=slice(None,-1);b[axis]=slice(1,None);a=tuple(a);b=tuple(b)
        q=.003*dt*(head[a]-head[b]);q=np.where(blocked[a]|blocked[b],0,q)
        outgoing[a]+=np.maximum(q,0);outgoing[b]+=np.maximum(-q,0);transfers.append((a,b,q))
    boundary=np.zeros_like(water);boundary[-1]=np.where(blocked[-1],0,.0008*dt*water[-1]);outgoing+=boundary
    scale=np.minimum(1,np.divide(water,outgoing,out=np.ones_like(water),where=outgoing>0));result=water.copy()
    for a,b,q in transfers:
        q=np.where(q>=0,q*scale[a],q*scale[b]);result[a]-=q;result[b]+=q
    out=boundary*scale;result-=out
    residual=float((result.sum()-h.sum()-added.sum()+drain.sum()+out.sum())*dx*dx)
    return np.maximum(result,0),dict(rain_m3=float(added.sum()*dx*dx),drain_m3=float(drain.sum()*dx*dx),outflow_m3=float(out.sum()*dx*dx),residual_m3=residual)

def simulate(cfg):
    z,blocked=terrain(cfg);rng=np.random.default_rng(cfg.seed);h=np.zeros_like(z);frames=[];rain=[];budget=[];amp=rng.uniform(.85,1.15)
    for t in range(cfg.steps):
        r=cfg.intensity/3600000*max(0,np.sin(np.pi*t/cfg.steps))**2*amp
        h,b=step(z,h,r,cfg.dt,blocked=blocked);frames.append(h.copy());rain.append(r*3600000);budget.append(b)
    return dict(z=z,blocked=blocked,depth=np.array(frames),rain=np.array(rain),budget=budget,dt=cfg.dt)

def crossings(n):
    return [(int(n*r),int(n*c)) for r,c in [(.25,.45),(.38,.60),(.50,.40),(.63,.55),(.75,.45),(.86,.63)]]
