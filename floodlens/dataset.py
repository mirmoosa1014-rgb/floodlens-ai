import numpy as np
from .simulation import Config,simulate,crossings
from .policy import gauges,observations,features

def episode(family,seed,intensity,policy='information',steps=75):
    run=simulate(Config(seed=seed,family=family,intensity=intensity,steps=steps));sites=gauges(run['z'],policy,seed);obs=observations(run,sites,seed+1000);X=[];y=[];persistence=[]
    for t in range(3,steps-3):
        for target in crossings(16):
            x=features(run,sites,obs,t,target);X.append(x);y.append(run['depth'][t+3,target[0],target[1]]);persistence.append(x[0])
    return np.array(X),np.array(y),np.array(persistence),run,sites,obs
