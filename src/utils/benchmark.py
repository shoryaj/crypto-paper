"""Run a deterministic 3x10x3x3 sweep, each check with a 30-second timeout.

RSS before/after is a process snapshot, NOT peak memory or isolated overhead.
Z3 statistics are preserved per query. Repeats share one process; no claims
of statistically significant comparisons or production throughput are made.
"""
import csv
import json
import platform
from pathlib import Path
import psutil
import z3
from case_studies.bzx_exploit import run
from case_studies.harvest_exploit import run as harvest
from case_studies.euler_exploit import run as euler
from src.core.verifier import replay
from src.core.analysis import derive, optimal_candidates, sufficient_liquidity
from src.core.uint256 import check_roundtrip


def main():
    out=Path('results'); out.mkdir(exist_ok=True)
    queries=out/'queries'; queries.mkdir(exist_ok=True)
    records=[]; rows=[]
    process=psutil.Process()
    for reserve in [100,1000,10000]:
        for ltv_int in range(50,96,5):
            ltv=str(ltv_int/100)
            for fee in ['0.0009','0.0015','0.003']:
                for repeat in range(3):
                    v=run(x_init=reserve,y_init=reserve,ltv_val=ltv,fee_rate=fee)
                    before=process.memory_info().rss
                    result=v.verify_economic_invariant(queries/f'{len(records):04}.smt2')
                    after=process.memory_info().rss
                    analytic=optimal_candidates(reserve,reserve,100,ltv,fee,1000,400)
                    result['analytic']=analytic
                    result['replayed']=replay(result) if result['status']=='sat' else None
                    if result['status'] != 'unknown':
                        assert (result['status']=='sat') == analytic['profitable']
                    if result['status']=='sat':
                        assert result['replayed']
                    records.append(result)
                    rows.append(dict(reserve=reserve,k=reserve**2,ltv=ltv,fee=fee,
                        repeat=repeat,status=result['status'],elapsed_ms=result['elapsed_ms'],
                        rss_before_bytes=before,rss_after_bytes=after,rss_delta_bytes=after-before))
    with (out/'sweep.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    (out/'sweep.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
    cases={'spot':run().verify_economic_invariant(),
        'bounded':run('bounded',epsilon='0.1').verify_economic_invariant(),
        'loose_bound':run('bounded',epsilon='1').verify_economic_invariant(),
        'dynamic':run('dynamic').verify_economic_invariant(),
        'harvest_proxy':harvest(), 'harvest_fixed':harvest(True),
        'euler_health':euler(), 'euler_fixed':euler(True),
        'uint256':check_roundtrip(1000,1000,100),
        'symbolic_derivation':derive(),
        'liquidity_bound':sufficient_liquidity(100,'0.75','0.0009',1000)}
    (out/'cases.json').write_text(json.dumps(cases,indent=2),encoding='utf-8')
    (out/'environment.json').write_text(json.dumps(dict(python=platform.python_version(),
        platform=platform.platform(),processor=platform.processor(),z3=z3.get_version_string(),
        repeats=3,flash_cap=1000,lending_cash=400,collateral=100,
        memory_metric='process RSS snapshots; not peak or isolated solver overhead'),indent=2),encoding='utf-8')
    print(json.dumps({'queries':len(rows),'counts':{s:sum(r['status']==s for r in rows)
                      for s in ['sat','unsat','unknown']}},indent=2))


if __name__=='__main__':
    main()
