"""Produce static publication figures from measured CSV, never invented data."""
import csv
import os
import tempfile
from pathlib import Path
from statistics import median
os.environ.setdefault('MPLCONFIGDIR', str(Path(tempfile.gettempdir())/'defi-verifier-mpl'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    rows=list(csv.DictReader(Path('results/sweep.csv').open(encoding='utf-8')))
    fig,axes=plt.subplots(1,2,figsize=(9,3.4),layout='constrained')
    for reserve in sorted({int(r['reserve']) for r in rows}):
        ltvs=sorted({float(r['ltv']) for r in rows})
        times=[median(float(r['elapsed_ms']) for r in rows
                if int(r['reserve'])==reserve and float(r['ltv'])==ltv) for ltv in ltvs]
        axes[0].plot(ltvs,times,marker='o',label=f'x=y={reserve}')
        fractions=[sum(r['status']=='sat' for r in rows if int(r['reserve'])==reserve and float(r['ltv'])==ltv)/
                   sum(1 for r in rows if int(r['reserve'])==reserve and float(r['ltv'])==ltv) for ltv in ltvs]
        axes[1].plot(ltvs,fractions,marker='o',label=f'x=y={reserve}')
    axes[0].set(xlabel='LTV',ylabel='Median solve time (ms)',yscale='log')
    axes[1].set(xlabel='LTV',ylabel='Fraction SAT across fees and repeats',ylim=(-.05,1.05))
    for ax in axes:
        ax.grid(alpha=.2); ax.legend(fontsize=8)
    Path('paper/figures').mkdir(parents=True,exist_ok=True)
    fig.savefig('paper/figures/sweep.pdf')
    fig.savefig('paper/figures/sweep.png',dpi=180)


if __name__=='__main__':
    main()
