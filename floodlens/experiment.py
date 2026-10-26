import argparse,csv,json
from pathlib import Path
import numpy as np
from .dataset import episode
from .model import fit,predict
from .policy import route,inspection_events,assimilate
ROOT=Path(__file__).resolve().parents[1]
def lead_time(truth,pred,threshold=.015):
    y=truth.reshape(-1,6);q=pred.reshape(-1,6);leads=[]
    for c in range(6):
        onset=np.flatnonzero(y[:,c]>=threshold)
        if not len(onset):continue
        at=int(onset[0])+3;alarms=np.flatnonzero(q[:,c]>=threshold);early=alarms[alarms<=at]
        leads.append((at-int(early[0]))*20 if len(early) else 0)
    return float(np.mean(leads)) if leads else 0.
def score(b,q):
    truth=b>=.015;alarm=q>=.015
    return dict(mae_m=float(np.mean(abs(q-b))),recall=float(np.sum(alarm&truth)/max(1,np.sum(truth))),false_alert_rate=float(np.sum(alarm&~truth)/max(1,np.sum(~truth))),lead_time_s=lead_time(b,q))
def main(quick=False):
    train_families=list(range(4 if quick else 6));val_families=[10,11];test_families=[20,21] if quick else [20,21,22,23];X=[];Y=[]
    for fam in train_families:
        for seed in range(2 if quick else 4):
            a,b,*_=episode(fam,seed,35+seed*22);X.extend(a);Y.extend(b)
    m=fit(np.array(X),np.array(Y));res=[]
    for fam in val_families:
        a,b,*_=episode(fam,40+fam,80);res.extend(abs(predict(m,a)-b))
    m['interval90_m']=float(np.quantile(res,.90));m['train_families']=train_families;m['validation_families']=val_families;m['test_families']=test_families
    ROOT.joinpath('models/nowcast.json').write_text(json.dumps(m,indent=2));rows=[];route_rows=[]
    for fam in test_families:
        for storm,intensity in [('heldout',70),('ood',150)]:
            for policy in ['random','grid','information']:
                a,b,p,run,sites,obs=episode(fam,60+fam,intensity,policy);pred=predict(m,a)
                for name,q in [('ridge',pred),('interpolation',p),('persistence',np.maximum(0,p-a[:,1]))]:
                    rows.append(dict(family=fam,storm=storm,policy=policy,model=name,**score(b,q),coverage90=float(np.mean(abs(q-b)<=m['interval90_m']))))
                for kind in ['priority','nearest']:
                    # First issue is t=3; planning uses that issue only. No hidden target access.
                    plan=route(run['z'],pred[:6],kind=kind);ev=inspection_events(run,plan,1060+fam,start_s=60)
                    # Predictions start at simulation t=3; align acquisition steps to this index.
                    aligned=[dict(e,available_step=e['available_step']-3) for e in ev]
                    updated=assimilate(pred.reshape(-1,6),aligned).reshape(-1)
                    route_rows.append(dict(family=fam,storm=storm,policy=policy,route=kind,distance_m=plan['distance_m'],duration_s=plan['duration_s'],unvisited=len(plan['missed']),**score(b,updated)))
    for file,data in [('metrics.csv',rows),('route_metrics.csv',route_rows)]:
        with ROOT.joinpath('results',file).open('w') as f:
            w=csv.DictWriter(f,fieldnames=data[0]);w.writeheader();w.writerows(data)
    summary={'mode':'quick' if quick else 'full','train_rows':len(Y),'episodes_test':len(test_families)*2*3,'split':{'train':train_families,'validation':val_families,'test':test_families},'model_mae_m':{name:float(np.mean([r['mae_m'] for r in rows if r['model']==name])) for name in ['ridge','interpolation','persistence']},'coverage90':float(np.mean([r['coverage90'] for r in rows if r['model']=='ridge'])),'max_mass_residual_m3':max(abs(b['residual_m3']) for b in run['budget']),'route_mae_m':{k:float(np.mean([r['mae_m'] for r in route_rows if r['route']==k])) for k in ['priority','nearest']},'route':route(run['z'],pred[:6])}
    ROOT.joinpath('results/summary.json').write_text(json.dumps(summary,indent=2));from .visuals import render;render(rows,run,sites,obs,summary);print(json.dumps(summary,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--quick',action='store_true');main(p.parse_args().quick)
