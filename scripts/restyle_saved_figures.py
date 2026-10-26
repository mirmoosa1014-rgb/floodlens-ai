"""Render the Paper Cut evidence figures from frozen saved artifacts only.

No simulation, training, fitted coefficients or numerical output files are written.
"""
from pathlib import Path
import csv,json,sys
import numpy as np
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
from floodlens.visuals import render
saved=np.load(root/'results/representative.npz')
rows=list(csv.DictReader((root/'results/metrics.csv').open()))
for row in rows:
    for key in ['mae_m','recall','false_alert_rate','lead_time_s','coverage90']:
        row[key]=float(row[key])
summary=json.loads((root/'results/summary.json').read_text())
render(rows,{'z':saved['terrain'],'depth':saved['depth']},saved['sites'],saved['observations'],summary)
exec(compile((root/'scripts/render_evaluation.py').read_text(),str(root/'scripts/render_evaluation.py'),'exec'),{'__file__':str(root/'scripts/render_evaluation.py'),'__name__':'__main__'})
exec(compile((root/'scripts/render_animation.py').read_text(),str(root/'scripts/render_animation.py'),'exec'),{'__file__':str(root/'scripts/render_animation.py'),'__name__':'__main__'})
