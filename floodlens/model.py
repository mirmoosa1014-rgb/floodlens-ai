"""Small ridge regression; JSON weights avoid untrusted pickle loading."""
import json
from pathlib import Path
import numpy as np
FEATURES=['interpolated_depth_m','recent_delta_m','rain_100mm_h','trailing_rain_100mm_h','target_elevation_m','gauge_elevation_m','nearest_sensor_cells_normalized','depth_rain_interaction']
def fit(X,y):
    X=np.asarray(X,dtype=float);y=np.asarray(y,dtype=float)
    if X.ndim!=2 or X.shape[1]!=len(FEATURES) or len(X)==0 or y.shape!=(len(X),):raise ValueError('nonempty eight-feature rows and matching scalar targets required')
    if not np.isfinite(X).all() or not np.isfinite(y).all():raise ValueError('training data must be finite')
    mu=X.mean(0);scale=X.std(0);scale[scale<1e-8]=1
    A=np.column_stack([np.ones(len(X)),(X-mu)/scale]);penalty=np.eye(A.shape[1])*.05;penalty[0,0]=0
    weights=np.linalg.solve(A.T@A+penalty,A.T@y)
    return dict(feature_schema=FEATURES,mean=mu.tolist(),scale=scale.tolist(),weights=weights.tolist(),horizon_steps=3,interval90_m=None)
def predict(model,X):
    X=np.asarray(X);return np.maximum(0,np.column_stack([np.ones(len(X)),(X-model['mean'])/model['scale']])@model['weights'])
def load(path):
    m=json.loads(Path(path).read_text())
    if m['feature_schema']!=FEATURES:raise ValueError('Model schema mismatch')
    for key,length in [('mean',8),('scale',8),('weights',9)]:
        values=np.asarray(m[key],dtype=float)
        if values.shape!=(length,) or not np.isfinite(values).all():raise ValueError('Invalid model vector: '+key)
        if key=='scale' and np.any(values<=0):raise ValueError('Model scales must be positive')
        m[key]=values.tolist()
    return m
