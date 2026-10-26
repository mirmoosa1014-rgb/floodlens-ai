from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
if 'floodlens_paper' not in matplotlib.colormaps:
    matplotlib.colormaps.register(LinearSegmentedColormap.from_list('floodlens_paper',['#FFF8F0','#2F6F6A']))
ROOT=Path(__file__).resolve().parents[1]
def render(rows,run,sites,obs,summary):
    plt.rcParams.update({'font.family':'DejaVu Serif','figure.facecolor':'#E7D7C3','axes.facecolor':'#FFF8F0','text.color':'#2A2118','axes.labelcolor':'#7A6556','xtick.color':'#7A6556','ytick.color':'#7A6556','axes.edgecolor':'#7A6556','font.size':10,'axes.prop_cycle':plt.cycler(color=['#3E6BA8','#E25B45','#2F6F6A']),'legend.edgecolor':'#E7D7C3'})
    fig=plt.figure(figsize=(14,8),layout='constrained');gs=fig.add_gridspec(2,3)
    ax=fig.add_subplot(gs[:,0],projection='3d');y,x=np.mgrid[:16,:16];ax.plot_surface(x*12,y*12,run['z']+run['depth'][-1],cmap='floodlens_paper',alpha=.95)
    for axis in [ax.xaxis,ax.yaxis,ax.zaxis]:axis.set_pane_color((1,.9725,.9412,1))
    ax.set(xlabel='East (m)',ylabel='North (m)',zlabel='Surface (m)',title='Synthetic terrain + water surface');ax.view_init(35,-55)
    ax=fig.add_subplot(gs[0,1]);im=ax.imshow(run['depth'][-1],cmap='floodlens_paper',vmin=0,vmax=.09);ax.scatter([s[1] for s in sites],[s[0] for s in sites],c='#E25B45',marker='^',label='Gauges');ax.legend();ax.set_title('Water depth and virtual sensors');fig.colorbar(im,ax=ax,label='Depth (m)')
    ax=fig.add_subplot(gs[0,2]);names=list(summary['model_mae_m']);ax.barh(names,[summary['model_mae_m'][n]*1000 for n in names],color=['#2F6F6A','#3E6BA8','#E25B45']);ax.set(xlabel='Mean absolute error (mm)',title='Paired heldout + OOD episodes')
    ax=fig.add_subplot(gs[1,1]);t=np.arange(len(obs))*20/60
    for i in range(3):ax.plot(t,obs[:,i]*1000,label=f'Gauge {i+1}')
    ax.set(xlabel='Elapsed time (min)',ylabel='Observed depth (mm)',title='Noisy virtual measurements');ax.legend(fontsize=8)
    ax=fig.add_subplot(gs[1,2]);policies=['random','grid','information'];values=[np.mean([r['mae_m'] for r in rows if r['policy']==p and r['model']=='ridge'])*1000 for p in policies];ax.bar(policies,values,color=['#3E6BA8','#E25B45','#2F6F6A']);ax.set(ylabel='MAE (mm)',title='Gauge placement • equal budget = 3');ax.tick_params(axis='x',rotation=12)
    fig.suptitle('FLOODLENS / Synthetic observation laboratory',fontsize=20,fontweight='bold',y=1.10);fig.savefig(ROOT/'docs/images/hero.png',dpi=150,bbox_inches='tight',pad_inches=.25);plt.close(fig)
