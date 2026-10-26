"""Small data-backed animation from saved representative depths; no synthetic imagery."""
from pathlib import Path
from io import BytesIO
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
root=Path(__file__).resolve().parents[1];r=np.load(root/'results/representative.npz');frames=[]
for t in range(0,len(r['depth']),5):
 fig,ax=plt.subplots(figsize=(6,5),facecolor='#071827');ax.set_facecolor('#0c2334');im=ax.imshow(r['depth'][t],cmap='Blues',vmin=0,vmax=.09,extent=(0,192,192,0));ax.scatter(r['sites'][:,1]*12,r['sites'][:,0]*12,c='#e4a846',marker='^',s=45)
 ax.set(xlabel='East (m)',ylabel='North (m)',title=f'SYNTHETIC ONLY / elapsed {t*20/60:.1f} min');ax.xaxis.label.set_color('#d3e8ef');ax.yaxis.label.set_color('#d3e8ef');ax.title.set_color('#d3e8ef');ax.tick_params(colors='#b6ccd9');cb=fig.colorbar(im,ax=ax,label='Water depth (m)');cb.ax.yaxis.label.set_color('#d3e8ef');cb.ax.tick_params(colors='#b6ccd9');fig.tight_layout();buf=BytesIO();fig.savefig(buf,format='png',dpi=90);buf.seek(0);frames.append(Image.open(buf).convert('RGB'));plt.close(fig)
frames[0].save(root/'docs/images/storm.gif',save_all=True,append_images=frames[1:],duration=160,loop=0)
