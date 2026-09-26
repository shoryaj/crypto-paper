from pathlib import Path
from fractions import Fraction
from collections import defaultdict
from statistics import median
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'paper/figures'
rows=json.loads((ROOT/'results/sweep.json').read_text())
navy='#17324D'; teal='#087F8C'; coral='#B74735'; gold='#B47B14'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.labelcolor':navy,'text.color':navy,'axes.spines.top':False,'axes.spines.right':False,'axes.titleweight':'bold','pdf.fonttype':42})
groups=defaultdict(list)
for row in rows:
    p=row['parameters']
    key=(int(p['x']),float(Fraction(p['ltv'])),float(Fraction(p['fee'])))
    groups[key].append(row)
assert len(rows)==270 and len(groups)==90
assert all(len(v)==3 and len({r['status'] for r in v})==1 for v in groups.values())
reserves=sorted({k[0] for k in groups}); ltvs=sorted({k[1] for k in groups}); fees=sorted({k[2] for k in groups})
stats=[]
fig,axes=plt.subplots(1,2,figsize=(10,3.7),layout='constrained',gridspec_kw={'width_ratios':[1,1.3]})
sat=[]; unsat=[]
for reserve in reserves:
    statuses=[v[0]['status'] for k,v in groups.items() if k[0]==reserve]
    sat.append(statuses.count('sat'));unsat.append(statuses.count('unsat'))
    times=[r['elapsed_ms'] for k,v in groups.items() if k[0]==reserve for r in v]
    stats.append({'reserve':reserve,'settings':len(statuses),'sat':sat[-1],'unsat':unsat[-1],'min_ms':min(times),'median_ms':median(times),'p95_ms':float(np.percentile(times,95)),'max_ms':max(times)})
x=np.arange(3)
axes[0].bar(x,sat,color=coral,label='SAT: positive extraction')
axes[0].bar(x,unsat,bottom=sat,color=teal,label='UNSAT: excluded in model')
for i in x:
    if sat[i]:axes[0].text(i,sat[i]/2,str(sat[i]),ha='center',va='center',color='white',weight='bold')
    if unsat[i]:axes[0].text(i,sat[i]+unsat[i]/2,str(unsat[i]),ha='center',va='center',color='white',weight='bold')
axes[0].set(xticks=x,xticklabels=['100','1,000','10,000'],xlabel='Equal reserves x = y',ylabel='Distinct parameter settings',ylim=(0,33),title='A  |  Decisions for 90 settings')
axes[0].legend(loc='upper center',bbox_to_anchor=(.5,-.2),frameon=False,fontsize=8)
for i,reserve in enumerate(reserves):
    rr=[r for k,v in groups.items() if k[0]==reserve for r in v]
    values=[r['elapsed_ms'] for r in rr]
    jitter=np.random.default_rng(100+i).uniform(-.17,.17,len(values))
    axes[1].scatter(i+jitter,values,s=13,alpha=.45,color=[coral if r['status']=='sat' else teal for r in rr],edgecolors='none')
    axes[1].plot([i-.25,i+.25],[median(values)]*2,color=navy,linewidth=2.5)
axes[1].set(xticks=x,xticklabels=['100','1,000','10,000'],xlabel='Equal reserves x = y',ylabel='Solver check time (ms, log scale)',yscale='log',title='B  |  All 270 recorded checks')
axes[1].grid(axis='y',alpha=.2)
axes[1].text(.5,-.27,'Each dot is one check; navy lines mark medians.',transform=axes[1].transAxes,ha='center',fontsize=8)
fig.savefig(OUT/'color-measured-overview.pdf',bbox_inches='tight');fig.savefig(OUT/'color-measured-overview.png',dpi=220,bbox_inches='tight');plt.close(fig)

fig,axes=plt.subplots(1,3,figsize=(10,4.5),layout='constrained')
for ax,reserve in zip(axes,reserves):
    matrix=np.array([[groups[(reserve,l,f)][0]['status']=='sat' for f in fees] for l in ltvs],dtype=int)
    ax.imshow(matrix,cmap=ListedColormap([teal,coral]),vmin=0,vmax=1,aspect='auto')
    for i in range(10):
        for j in range(3):ax.text(j,i,'S' if matrix[i,j] else 'U',color='white',ha='center',va='center',weight='bold',fontsize=10)
    ax.set(xticks=range(3),xticklabels=['0.09%','0.15%','0.30%'],yticks=range(10),yticklabels=[f'{l:.2f}' for l in ltvs],xlabel='Flash fee',ylabel='Loan-to-value limit',title=f'x = y = {reserve:,}')
    ax.set_xticks(np.arange(-.5,3,1),minor=True);ax.set_yticks(np.arange(-.5,10,1),minor=True);ax.grid(which='minor',color='white',linewidth=1.5);ax.tick_params(which='minor',length=0)
fig.savefig(OUT/'color-decision-map.pdf',bbox_inches='tight');fig.savefig(OUT/'color-decision-map.png',dpi=220,bbox_inches='tight');plt.close(fig)
(ROOT/'paper/color-statistics.json').write_text(json.dumps(stats,indent=2))
print(json.dumps(stats,indent=2))
