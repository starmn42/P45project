"""Pre-result EXP-003 feature calculator; no outcome access occurs here."""
from __future__ import annotations
from typing import Iterable,Mapping,Any
from p45_v27.integrity import sha256_json

VERSION='EXP003-CALCULATOR-1.0';DISTANCES=tuple(range(45));BANDS=((1,10),(11,20),(21,30),(31,40),(41,45))

def build_feature_state(previous_main:Iterable[int],evaluation_round:int)->dict[str,Any]:
    main=tuple(sorted(set(int(x) for x in previous_main)))
    if len(main)!=6 or any(x<1 or x>45 for x in main):raise ValueError('previous MAIN must contain 6 unique numbers in 1..45')
    distances={n:min(abs(n-m) for m in main) for n in range(1,46)}
    exposures={d:sum(v==d for v in distances.values()) for d in DISTANCES}
    occupied=[i for i,(lo,hi) in enumerate(BANDS) if any(lo<=m<=hi for m in main)]
    payload={'version':VERSION,'evaluation_round':evaluation_round,'source_end_round':evaluation_round-1,'previous_main':main,'number_distance':distances,'distance_exposure':exposures,'previous_occupied_bands':occupied,'distance_range':DISTANCES,'bands':BANDS}
    return {**payload,'feature_hash':sha256_json(payload)}

def evaluate_locked_feature(feature:Mapping[str,Any],main:Iterable[int],bonus:int)->dict[str,Any]:
    current=tuple(sorted(set(int(x) for x in main)))
    if len(current)!=6 or any(x<1 or x>45 for x in current) or bonus in current or not 1<=bonus<=45:raise ValueError('invalid outcome')
    distances={int(k):int(v) for k,v in feature['number_distance'].items()}
    main_hits={d:sum(distances[n]==d for n in current) for d in DISTANCES}
    integrated=current+(bonus,);integrated_hits={d:sum(distances[n]==d for n in integrated) for d in DISTANCES}
    current_bands={i for i,(lo,hi) in enumerate(BANDS) if any(lo<=n<=hi for n in current)};previous=set(feature['previous_occupied_bands'])
    band_transition={i:('MAINTAIN' if i in previous and i in current_bands else 'EXIT' if i in previous else 'ENTRY' if i in current_bands else 'EMPTY') for i in range(len(BANDS))}
    payload={'evaluation_round':feature['evaluation_round'],'feature_hash':feature['feature_hash'],'main_hits':main_hits,'integrated_hits':integrated_hits,'band_transition':band_transition}
    return {**payload,'outcome_hash':sha256_json(payload)}
