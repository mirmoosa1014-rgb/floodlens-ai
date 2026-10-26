"""Supplementary evidence panels, using only saved benchmark outputs."""
from pathlib import Path
import csv,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
if 'floodlens_paper' not in matplotlib.colormaps:
    matplotlib.colormaps.register(LinearSegmentedColormap.from_list('floodlens_paper',['#FFF8F0','#2F6F6A']))
root=Path(__file__).resolve().parents[1]
rows=list(csv.DictReader((root/'results/metrics.csv').open()));routes=list(csv.DictReader((root/'results/route_metrics.csv').open()))
plt.rcParams.update({'figure.facecolor':'#E7D7C3','axes.facecolor':'#FFF8F0','text.color':'#2A2118','axes.labelcolor':'#7A6556','xtick.color':'#7A6556','ytick.color':'#7A6556','axes.edgecolor':'#7A6556','font.size':10})
fig,ax=plt.subplots(1,3,figsize=(14,4),layout='constrained')
names=['ridge','interpolation','persistence'];colors=['#2F6F6A','#3E6BA8','#E25B45']
for i,(name,color) in enumerate(zip(names,colors)):
 values=[float(r['mae_m'])*1000 for r in rows if r['model']==name];ax[0].scatter(np.full(len(values),i)+np.linspace(-.12,.12,len(values)),values,color=color,alpha=.75,s=25)
ax[0].set_xticks(range(3),names);ax[0].set(ylabel='Scenario MAE (mm)',title='Failure variability across paired episodes')
vals=[np.mean([float(r['coverage90']) for r in rows if r['model']=='ridge' and r['storm']==s])*100 for s in ['heldout','ood']];ax[1].bar(['Heldout','OOD'],vals,color=['#2F6F6A','#E25B45']);ax[1].axhline(90,color='#7A6556',linestyle='--',label='Nominal 90%');ax[1].set(ylim=(0,105),ylabel='Empirical interval coverage (%)',title='Calibration degrades under shift');ax[1].legend()
for i,name in enumerate(['priority','nearest']):
 group=[r for r in routes if r['route']==name];ax[2].scatter([float(r['distance_m']) for r in group],[float(r['mae_m'])*1000 for r in group],label=name,color=colors[i],alpha=.75)
ax[2].set(xlabel='Inspection travel including return (m)',ylabel='Updated forecast MAE (mm)',title='Equal 420 m / 120 s inspection budgets');ax[2].legend()
fig.savefig(root/'docs/images/evaluation.png',dpi=160,bbox_inches='tight',pad_inches=.25)
