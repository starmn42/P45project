from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
import statistics
from collections import Counter
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / "v27_storage/audits/current_1239_predraw_rerun_001/STAGING_CONTIGUOUS_DRAW_1_1238.csv"
SOURCE_SHA_EXPECTED = "1160cafab32542f28b9f2e7656ec4b471d01a3a521b8b35e21dc9ae9c953cce8"
SCHEDULE_SHA_EXPECTED = "5f212342c6c27fca8eafbc75d20a55fc4be4ca2961a9c70c3a7af0eca26f1075"
NSIM = 20_000
SEED = 20_260_826

LSPC = [
[(0,3,9),(1,7,4),(2,5,11),(12,14,13),(6,10,8)],
[(6,9,0),(7,13,10),(8,11,2),(3,5,4),(1,12,14)],
[(0,12,6),(2,14,8),(4,13,1),(9,11,10),(3,7,5)],
[(3,6,12),(4,10,7),(5,8,14),(0,2,1),(9,13,11)],
[(1,10,13),(9,12,3),(11,14,5),(6,8,7),(0,4,2)],
[(1,3,2),(4,6,5),(7,9,8),(10,12,11),(0,13,14)],
[(2,4,3),(5,7,6),(8,10,9),(11,13,12),(1,14,0)],
[(2,6,4),(5,9,7),(8,12,10),(0,11,13),(3,14,1)],
[(0,1,8),(3,4,11),(6,7,14),(9,10,2),(12,13,5)],
[(1,2,9),(4,5,12),(7,8,0),(10,11,3),(13,14,6)],
[(2,3,10),(5,6,13),(8,9,1),(11,12,4),(0,14,7)],
[(0,5,10),(3,8,13),(6,11,1),(9,14,4),(2,12,7)],
[(1,6,11),(4,9,14),(7,12,2),(0,10,5),(3,13,8)],
[(2,7,12),(5,10,0),(8,13,3),(1,11,6),(4,14,9)],
[(0,7,11),(3,10,14),(6,13,2),(1,9,5),(4,12,8)],
[(1,8,12),(4,11,0),(7,14,3),(2,10,6),(5,13,9)],
[(2,9,13),(5,12,1),(0,8,4),(3,11,7),(6,14,10)],
]
PARTIAL = [
([(3,9,6),(4,7,13),(5,11,8),(10,14,12)], (0,1,2)),
([(6,12,9),(7,10,1),(8,14,11),(2,13,0)], (3,4,5)),
([(0,9,12),(2,11,14),(10,13,4),(1,5,3)], (6,7,8)),
([(1,13,7),(3,12,0),(5,14,2),(4,8,6)], (9,10,11)),
([(0,6,3),(1,4,10),(2,8,5),(7,11,9)], (12,13,14)),
]
PATTERNS = [(0,1,3),(1,2,4),(2,3,5),(3,4,6),(4,5,0),(5,6,1),(6,0,2)]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def number(x: int, i: int) -> int:
    return x + 1 + 15 * i


def cblock(cell, i):
    x, y, z = cell
    return tuple(sorted((number(x, i), number(y, i), number(z, (i + 1) % 3))))


def ablock(x):
    return (number(x, 0), number(x, 1), number(x, 2))


def build_schedule():
    classes = []
    for cells in LSPC:
        classes.append(sorted(cblock(cell, i) for cell in cells for i in range(3)))
    for cells, tset in PARTIAL:
        classes.append(sorted([cblock(cell, i) for cell in cells for i in range(3)] + [ablock(x) for x in tset]))
    return classes


def verify_schedule(classes):
    trios = [t for cls in classes for t in cls]
    pairs = Counter(tuple(sorted(p)) for t in trios for p in itertools.combinations(t, 2))
    nums = Counter(n for t in trios for n in t)
    checks = {
        "parallel_classes_22": len(classes) == 22,
        "each_class_15": all(len(c) == 15 for c in classes),
        "each_class_partitions_1_45": all(sorted(n for t in c for n in t) == list(range(1,46)) for c in classes),
        "total_trios_330": len(trios) == 330,
        "unique_trios_330": len(set(trios)) == 330,
        "unordered_pairs_990": len(pairs) == 990,
        "each_pair_once": set(pairs.values()) == {1},
        "each_number_22": len(nums) == 45 and set(nums.values()) == {22},
        "no_within_trio_duplicate": all(len(set(t)) == 3 for t in trios),
        "number_range_1_45": all(1 <= n <= 45 for t in trios for n in t),
        "latin_cells_valid": all(z == (8*(x+y)) % 15 for cells in LSPC for x,y,z in cells),
    }
    if not all(checks.values()):
        raise RuntimeError(f"KTS invariant failure: {checks}")
    return checks, pairs, nums


def write_schedule(classes):
    path = OUT / "P45_TRIO_ORBIT_V1_KTS45_SCHEDULE_001.csv"
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["class_id","trio_id","n1","n2","n3"])
        for ci, cls in enumerate(classes, 1):
            for ti, t in enumerate(cls, 1):
                w.writerow([ci,ti,*t])
    got = sha256(path)
    if got != SCHEDULE_SHA_EXPECTED:
        raise RuntimeError(f"schedule hash mismatch: {got} != {SCHEDULE_SHA_EXPECTED}")
    return path, got


def load_draws():
    if sha256(SOURCE) != SOURCE_SHA_EXPECTED:
        raise RuntimeError("canonical source hash mismatch")
    rows = []
    with SOURCE.open(encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            rows.append({"round": int(r["round"]), "date": r["date"], "main": tuple(int(r[f"n{i}"]) for i in range(1,7)), "bonus": int(r["bonus"])})
    rounds = [r["round"] for r in rows]
    checks = {
        "continuity": rounds == list(range(rounds[0], rounds[-1]+1)),
        "duplicate_rounds_0": len(rounds) == len(set(rounds)),
        "main_errors_0": all(len(set(r["main"])) == 6 and all(1 <= n <= 45 for n in r["main"]) for r in rows),
        "bonus_range_errors_0": all(1 <= r["bonus"] <= 45 for r in rows),
        "bonus_main_overlap_0": all(r["bonus"] not in r["main"] for r in rows),
    }
    if not all(checks.values()):
        raise RuntimeError(f"data preflight failure: {checks}")
    return rows, checks


def fixed_schedule(classes):
    return [tuple(cls[i:i+3]) for cls in classes for i in range(0,15,3)]


class Linked:
    def __init__(self, classes):
        self.classes = classes
        self.used = set()
        self.pointer = 0
        self.resets = 0
        self.last_reset_target = 1
        self.output_num_counts = Counter()
        self.output_pair_counts = Counter()
        self.output_trio_counts = Counter()
        self.reset_rows = []
        self.maps = []
        self.global_ids = []
        gid = 0
        for cls in classes:
            mp, ids = {}, []
            for t in cls:
                ids.append(gid)
                for n in t: mp[n] = gid
                gid += 1
            self.maps.append(mp)
            self.global_ids.append(ids)
        self.trio_by_gid = [t for cls in classes for t in cls]

    def select(self, anchors, target):
        pointer_before = self.pointer
        reset = False
        selected = None
        for attempt in range(2):
            for off in range(22):
                k = (self.pointer + off) % 22
                gids = tuple(self.maps[k][a] for a in anchors)
                if len(set(gids)) == 3 and all(g not in self.used for g in gids):
                    selected = (k, gids)
                    break
            if selected is not None: break
            if attempt == 0:
                before = len(self.used)
                pair_repeats = sum(v-1 for v in self.output_pair_counts.values() if v > 1)
                trio_repeats = sum(v-1 for v in self.output_trio_counts.values() if v > 1)
                self.resets += 1
                self.reset_rows.append({
                    "reset_index": self.resets, "reset_target": target,
                    "rounds_since_previous_reset": target-self.last_reset_target,
                    "used_before": before, "unused_before": 330-before,
                    "number_exposure_counts": " ".join(f"{n}:{self.output_num_counts[n]}" for n in range(1,46)),
                    "pair_repeat_count": pair_repeats, "trio_repeat_count": trio_repeats,
                })
                self.last_reset_target = target
                self.used.clear()
                reset = True
        if selected is None:
            raise RuntimeError(f"linked design error after reset at target {target}")
        k, gids = selected
        trios = tuple(self.trio_by_gid[g] for g in gids)
        self.used.update(gids)
        self.pointer = (k+1) % 22
        for t in trios:
            self.output_trio_counts[t] += 1
            for n in t: self.output_num_counts[n] += 1
            for p in itertools.combinations(t,2): self.output_pair_counts[tuple(sorted(p))] += 1
        return trios, pointer_before, k, reset, self.pointer, len(self.used)


def hit_count(trio, mainset):
    return len(set(trio) & mainset)


def run_actual(rows, classes):
    fixed = fixed_schedule(classes)
    linked = Linked(classes)
    trace = []
    fixed_success = linked_success = 0
    fixed_any2 = linked_any2 = 0
    fixed_trio2 = linked_trio2 = 0
    paired = Counter()
    leakage = 0
    for idx, target in enumerate(range(2, rows[-1]["round"]+1)):
        prev, cur = rows[target-2], rows[target-1]
        if prev["round"] != target-1 or cur["round"] != target: leakage += 1
        seven = tuple(sorted((*prev["main"], prev["bonus"])))
        pattern_i = (target-2) % 7
        anchors = tuple(seven[p] for p in PATTERNS[pattern_i])
        ftrios = fixed[idx % 110]
        ltrios, pb, sc, reset, pa, used_n = linked.select(anchors, target)
        mset = set(cur["main"])
        fh = tuple(hit_count(t,mset) for t in ftrios)
        lh = tuple(hit_count(t,mset) for t in ltrios)
        fs, ls = max(fh)==3, max(lh)==3
        fixed_success += fs; linked_success += ls
        paired[(fs,ls)] += 1
        fixed_any2 += any(x==2 for x in fh); linked_any2 += any(x==2 for x in lh)
        fixed_trio2 += sum(x==2 for x in fh); linked_trio2 += sum(x==2 for x in lh)
        trace.append({
            "target_round":target,"source_round":target-1,"pattern_index":pattern_i+1,
            "sorted_previous_7":" ".join(map(str,seven)),"anchor_A":anchors[0],"anchor_B":anchors[1],"anchor_C":anchors[2],
            "pointer_before":pb+1,"selected_class":sc+1,
            "linked_A":" ".join(map(str,ltrios[0])),"linked_B":" ".join(map(str,ltrios[1])),"linked_C":" ".join(map(str,ltrios[2])),
            "reset_before_selection":"Y" if reset else "N","pointer_after":pa+1,"cumulative_reset_count":linked.resets,"used_trio_count_after":used_n,
            "fixed_A":" ".join(map(str,ftrios[0])),"fixed_B":" ".join(map(str,ftrios[1])),"fixed_C":" ".join(map(str,ftrios[2])),
            "fixed_hits_A":fh[0],"fixed_hits_B":fh[1],"fixed_hits_C":fh[2],"linked_hits_A":lh[0],"linked_hits_B":lh[1],"linked_hits_C":lh[2],
            "fixed_primary":int(fs),"linked_primary":int(ls),"fixed_any_exact2":int(any(x==2 for x in fh)),"linked_any_exact2":int(any(x==2 for x in lh)),
        })
    return {
        "fixed_primary":fixed_success,"linked_primary":linked_success,"paired":paired,
        "fixed_any2":fixed_any2,"linked_any2":linked_any2,"fixed_trio2":fixed_trio2,"linked_trio2":linked_trio2,
        "trace":trace,"linked":linked,"leakage":leakage,
    }


def mcnemar_exact(b, c):
    n = b+c
    if n == 0: return 1.0
    k = min(b,c)
    return min(1.0, 2*sum(math.comb(n,i) for i in range(k+1))/(2**n))


def simulate(classes, eval_rounds, observed_delta):
    fixed = fixed_schedule(classes)
    fixed_arr = np.array(fixed, dtype=np.int16) - 1
    maps = np.empty((22,46), dtype=np.int16)
    gids_by_class = np.empty((22,15), dtype=np.int16)
    gid = 0
    trio_by_gid = []
    for ci, cls in enumerate(classes):
        for ti,t in enumerate(cls):
            gids_by_class[ci,ti] = gid
            trio_by_gid.append(t)
            for n in t: maps[ci,n] = gid
            gid += 1
    trio_by_gid = np.array(trio_by_gid, dtype=np.int16)
    rng = np.random.default_rng(SEED)
    ge = 0
    deltas = Counter()
    batch_size = 100
    for start in range(0, NSIM, batch_size):
        bsz = min(batch_size, NSIM-start)
        keys = rng.random((bsz, eval_rounds+1, 45), dtype=np.float32)
        first7 = np.argpartition(keys, 7, axis=2)[:,:,:7]
        vals = first7 + 1
        order = np.take_along_axis(keys, first7, axis=2).argsort(axis=2)
        seq7 = np.take_along_axis(vals, order, axis=2)
        for h in range(bsz):
            used = np.zeros(330, dtype=np.bool_)
            pointer = 0
            fc = lc = 0
            for r in range(eval_rounds):
                prev7 = np.sort(seq7[h,r])
                anchors = prev7[list(PATTERNS[r%7])]
                selected = None
                for attempt in range(2):
                    for off in range(22):
                        ci = (pointer+off)%22
                        gs = maps[ci,anchors]
                        if len(set(gs.tolist())) == 3 and not used[gs].any():
                            selected = (ci,gs.copy()); break
                    if selected is not None: break
                    used[:] = False
                if selected is None: raise RuntimeError("simulation linked reset design error")
                ci,gs = selected; used[gs]=True; pointer=(ci+1)%22
                main = set(seq7[h,r+1,:6].tolist())
                fts = fixed_arr[r%110] + 1
                if any(sum(int(n) in main for n in t)==3 for t in fts): fc += 1
                if any(sum(int(n) in main for n in trio_by_gid[g])==3 for g in gs): lc += 1
            d = lc-fc
            deltas[d] += 1
            ge += d >= observed_delta
    return {"nsim":NSIM,"seed":SEED,"ge":ge,"p_one_sided":(1+ge)/(NSIM+1),"delta_distribution":dict(sorted(deltas.items()))}


def write_csv(path, rows):
    if not rows: return
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys()),lineterminator="\n")
        w.writeheader(); w.writerows(rows)


def main():
    classes=build_schedule()
    inv,_,_=verify_schedule(classes)
    schedule_path,schedule_sha=write_schedule(classes)
    rows,data_checks=load_draws()
    actual=run_actual(rows,classes)
    n=len(actual["trace"])
    delta=actual["linked_primary"]-actual["fixed_primary"]
    checkpoint_path = OUT / "P45_TRIO_ORBIT_V1_RESULT_001.json"
    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8")) if checkpoint_path.exists() else None
    if checkpoint and checkpoint.get("mc", {}).get("nsim") == NSIM and checkpoint.get("mc", {}).get("seed") == SEED and checkpoint.get("evaluated_rounds") == n and checkpoint.get("delta") == delta:
        mc = checkpoint["mc"]
    else:
        mc=simulate(classes,n,delta)
    b=actual["paired"][(True,False)]
    c=actual["paired"][(False,True)]
    intervals=[r["rounds_since_previous_reset"] for r in actual["linked"].reset_rows]
    used_before=[r["used_before"] for r in actual["linked"].reset_rows]
    exposures=list(actual["linked"].output_num_counts.values())
    pair_dist=Counter(actual["linked"].output_pair_counts.values())
    trio_dist=Counter(actual["linked"].output_trio_counts.values())
    judgment=("INCONCLUSIVE_LOW_SAMPLE" if n<1000 else "SUPPORTED" if delta>0 and mc["p_one_sided"]<=0.05 and actual["leakage"]==0 else "FAILED_NOT_SUPPORTED")
    write_csv(OUT/"P45_TRIO_ORBIT_V1_ROUND_TRACE_001.csv",actual["trace"])
    write_csv(OUT/"P45_TRIO_ORBIT_V1_RESET_TRACE_001.csv",actual["linked"].reset_rows)
    summary={
        "source":str(SOURCE),"source_sha256":sha256(SOURCE),"range":[rows[0]["round"],rows[-1]["round"]],"evaluated_rounds":n,
        "data_checks":data_checks,"schedule_sha256":schedule_sha,"invariants":inv,
        "fixed_primary":actual["fixed_primary"],"linked_primary":actual["linked_primary"],"delta":delta,
        "delta_percentage_points":100*delta/n,"relative_count_change_percent":100*delta/actual["fixed_primary"] if actual["fixed_primary"] else None,
        "paired":{"both_success":actual["paired"][(True,True)],"fixed_only":b,"linked_only":c,"both_fail":actual["paired"][(False,False)]},
        "mcnemar_exact_two_sided":mcnemar_exact(b,c),"mc":mc,
        "exact2":{"fixed_trio_count":actual["fixed_trio2"],"linked_trio_count":actual["linked_trio2"],"fixed_round_any":actual["fixed_any2"],"linked_round_any":actual["linked_any2"]},
        "resets":{"count":actual["linked"].resets,"interval_mean":statistics.mean(intervals) if intervals else None,"interval_median":statistics.median(intervals) if intervals else None,"interval_min":min(intervals) if intervals else None,"interval_max":max(intervals) if intervals else None,"mean_used_before":statistics.mean(used_before) if used_before else None},
        "exposure":{"number_min":min(exposures),"number_max":max(exposures),"number_std_population":statistics.pstdev(exposures)},
        "pair_output_frequency_distribution":dict(sorted(pair_dist.items())),"trio_output_frequency_distribution":dict(sorted(trio_dist.items())),
        "future_leakage":actual["leakage"],"final_judgment":judgment,
    }
    (OUT/"P45_TRIO_ORBIT_V1_RESULT_001.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
    report=f'''# P45 TRIO ORBIT V1 BACKTEST RESULT 001

## Final judgment

`{judgment}`

## Preflight

- Canonical source: `{SOURCE}`
- Canonical SHA-256: `{sha256(SOURCE)}`
- Data range / evaluated targets: `{rows[0]["round"]}..{rows[-1]["round"]} / 2..{rows[-1]["round"]} ({n})`
- Data checks: `{json.dumps(data_checks,ensure_ascii=False)}`
- KTS schedule SHA-256: `{schedule_sha}`
- Expected SHA match: `PASS`
- KTS invariants: `{json.dumps(inv,ensure_ascii=False)}`
- Future leakage: `{actual["leakage"]}`

## Primary exact 3/3

- Fixed: `{actual["fixed_primary"]}/{n} = {actual["fixed_primary"]/n:.9%}`
- Linked: `{actual["linked_primary"]}/{n} = {actual["linked_primary"]/n:.9%}`
- Delta linked-fixed: `{delta}` rounds; `{(actual["linked_primary"]-actual["fixed_primary"])/n:.9%}` percentage-point difference; `{100*delta/actual["fixed_primary"] if actual["fixed_primary"] else float("nan"):.6f}%` relative count change
- Paired both / fixed-only / linked-only / neither: `{actual["paired"][(True,True)]} / {b} / {c} / {actual["paired"][(False,False)]}`
- McNemar exact two-sided p: `{mcnemar_exact(b,c):.12g}`

## Fair-null Monte Carlo

- Histories / seed: `{NSIM} / {SEED}`
- Each history: `{n+1}` fair sequential MAIN6+BONUS draws, `{n}` evaluated targets
- Statistic: `linked_primary_count - fixed_primary_count`
- Simulated deltas >= observed: `{mc["ge"]}`
- One-sided plus-one p: `{mc["p_one_sided"]:.12g}`
- Simulation code SHA-256 is recorded in `SHA256SUMS_001.txt`.

## Separate exact 2/3 support

- Fixed exact2 TRIO count / rounds with at least one exact2: `{actual["fixed_trio2"]} / {actual["fixed_any2"]}`
- Linked exact2 TRIO count / rounds with at least one exact2: `{actual["linked_trio2"]} / {actual["linked_any2"]}`
- This support metric does not alter the primary judgment.

## Linked reset and exposure diagnostics

- Reset count: `{actual["linked"].resets}`
- Reset interval mean / median / min / max: `{summary["resets"]["interval_mean"]} / {summary["resets"]["interval_median"]} / {summary["resets"]["interval_min"]} / {summary["resets"]["interval_max"]}`
- Mean used TRIO count immediately before reset: `{summary["resets"]["mean_used_before"]}`
- Number exposure min / max / population std: `{summary["exposure"]["number_min"]} / {summary["exposure"]["number_max"]} / {summary["exposure"]["number_std_population"]:.9f}`
- Pair output-frequency distribution: `{json.dumps(summary["pair_output_frequency_distribution"],ensure_ascii=False)}`
- TRIO output-frequency distribution: `{json.dumps(summary["trio_output_frequency_distribution"],ensure_ascii=False)}`
- Per-reset details are in `P45_TRIO_ORBIT_V1_RESET_TRACE_001.csv`.

## Protection boundary

- OFFICIAL ENGINE / official gate / official DB / recommendation promotion: `UNCHANGED / 0 / 0 / NO`
- State / Decision / Registry / protected manifest changes: `0 / 0 / 0 / 0`
- This is an independent Experiment Lab result and is not evidence that an existing R-1 predictive signal succeeded.
'''
    (OUT/"P45_TRIO_ORBIT_V1_BACKTEST_RESULT_001.md").write_text(report,encoding="utf-8",newline="\n")
    manifest=[]
    for p in sorted(OUT.iterdir()):
        if p.is_file() and p.name not in {"SHA256SUMS_001.txt"}:
            manifest.append(f"{sha256(p)}  {p.name}")
    (OUT/"SHA256SUMS_001.txt").write_text("\n".join(manifest)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps(summary,ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()
