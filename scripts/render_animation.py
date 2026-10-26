"""Small data-backed animation from saved representative depths; no synthetic imagery."""
from pathlib import Path
from io import BytesIO
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
if 'floodlens_paper' not in matplotlib.colormaps:
    matplotlib.colormaps.register(LinearSegmentedColormap.from_list('floodlens_paper',['#FFF8F0','#2F6F6A']))
from PIL import Image
root=Path(__file__).resolve().parents[1];r=np.load(root/'results/representative.npz');frames=[]
for t in range(0,len(r['depth']),5):
 fig,ax=plt.subplots(figsize=(6,5),facecolor='#E7D7C3');ax.set_facecolor('#FFF8F0');im=ax.imshow(r['depth'][t],cmap='floodlens_paper',vmin=0,vmax=.09,extent=(0,192,192,0));ax.scatter(r['sites'][:,1]*12,r['sites'][:,0]*12,c='#E25B45',marker='^',s=45)
 ax.set(xlabel='East (m)',ylabel='North (m)',title=f'SYNTHETIC ONLY / elapsed {t*20/60:.1f} min');ax.xaxis.label.set_color('#2A2118');ax.yaxis.label.set_color('#2A2118');ax.title.set_color('#2A2118');ax.tick_params(colors='#7A6556');cb=fig.colorbar(im,ax=ax,label='Water depth (m)');cb.ax.yaxis.label.set_color('#2A2118');cb.ax.tick_params(colors='#7A6556');fig.tight_layout();buf=BytesIO();fig.savefig(buf,format='png',dpi=90);buf.seek(0);frames.append(Image.open(buf).convert('RGB'));plt.close(fig)
frames[0].save(root/'docs/images/storm.gif',save_all=True,append_images=frames[1:],duration=160,loop=0)
