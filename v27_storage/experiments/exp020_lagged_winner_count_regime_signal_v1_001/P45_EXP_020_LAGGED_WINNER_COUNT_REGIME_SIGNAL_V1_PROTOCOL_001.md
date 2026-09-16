# P45 EXP-020 — LAGGED WINNER-COUNT REGIME NEXT-DRAW NUMBER SIGNAL V1 — PROTOCOL 001

## Identity, hypothesis, and boundaries

- ID: `EXP-020 / EXP-DRAW-20260828-020-V1`.
- H1: a mechanically discovered contiguous integer regime of official `W_(T-1)` activates one fixed set of at most six numbers whose next-draw MAIN6 inclusion exceeds fair `6/45` through TRAIN, Selection, and untouched Holdout.
- Opposite: no candidate survives the locked stages or the one selected signal fails Holdout.
- Target T uses only round T-1 first-prize winning-game count. Target T own winner count is never used. Targets are `2..1238`; no 1239+ data.
- This is not EXP-019 rescue. It excludes sales, birthday range, Fixed, Linked, KTS, return-age, extinction, adjacency, pair, trio, sum, odd/even, prime, gap, ending digit, decade, and manual/auto features. `10..15` is only a user example and receives no preference.

## Locked sources and chronology

- Official rounds 1..1237: lexical `downloads/official-1-1237/raw/api-*.json`; round 1238: EXP-019 official raw JSONL.
- Combined raw proof SHA-256: `4ce76976f782d6ee06ea1d18eeab8420b1d3ef1e6f92f371ee0e8aa6a032e13f`, defined as SHA-256 of those lexical JSON bytes followed by EXP-019 JSONL bytes.
- Canonical MAIN6: `STAGING_CONTIGUOUS_DRAW_1_1238.csv`, SHA-256 `1160cafab32542f28b9f2e7656ec4b471d01a3a521b8b35e21dc9ae9c953cce8`.
- Require all 1,238 rounds, no missing MAIN6/winner count, no conflict or canonical mismatch; otherwise `EXP_020_PROTOCOL_BLOCKED_FULL_HISTORY_DATA_GAP` before relationship work.
- TRAIN-A `2..300` (299); TRAIN-B `301..600` (300); Selection `601..867` (267); Holdout `868..1238` (371).

## Exhaustive TRAIN discovery

- Let `[wmin,wmax]` be observed TRAIN `W_(T-1)` integer range. Enumerate every `[L,U]`, `wmin<=L<=U<=wmax`.
- Retain bands only when ACTIVE coverage is independently within inclusive `[10%,40%]` in both TRAIN halves. ACTIVE iff `L<=W_(T-1)<=U`.
- For every retained band, number n=1..45, and half h, compute exactly with `fractions.Fraction`: `DELTA_h=ACTIVE_HITS/ACTIVE_ROUNDS-INACTIVE_HITS/INACTIVE_ROUNDS`.
- Eligible numbers require both DELTA_A>0 and DELTA_B>0. Score `min(DELTA_A,DELTA_B)`; rank descending score then ascending number; choose at most six and never fill. Discard k=0.
- For frozen S, half h: `H_h=sum |S intersect MAIN6_T|` over active targets; `X_h=ACTIVE_ROUNDS_h*k`; `LIFT_h=H_h/X_h-6/45`.
- Retain only both lifts positive; `TRAIN_BAND_SCORE=min(LIFT_A,LIFT_B)`.
- Rank by descending exact score, ascending width U-L, ascending L, ascending U. Pass at most ten. No TRAIN p-value or evidence claim. Zero gives `FAILED_NO_TRAIN_CANDIDATE` and stops.

## Selection and exact null

- Evaluate only frozen top candidates on 601..867. Output frozen S only on active targets.
- Record active rounds A, exposures X=A*k, hits H, rate H/X and lift over 6/45.
- Exact null per active target is Hypergeometric(N=45,K=k,n=6). Convolve using integer DP weights `C(k,x)*C(45-k,6-x)` and denominator `C(45,6)`; exact upper p is tail integer weight divided by denominator^A. Monte Carlo is forbidden.
- Eligible iff A>=30, X>=90, rate>6/45, exact p<=1/10.
- Select exactly one by ascending exact p, descending exact lift, descending exact TRAIN score, ascending width, L, U. Zero eligible gives `FAILED_NO_SELECTION_SIGNAL` and stops.

## Immutable Selection Lock and Holdout

- Before Holdout relationship access, write immutable Selection Lock with experiment/protocol/source hashes, ranges, selected band/S/k, TRAIN-A/B and Selection statistics, timestamp, `Holdout relationship calculated=NO`, `FUTURE_LEAKAGE=0`; compute its SHA and never edit it.
- Apply only this locked signal to 868..1238 using W_(T-1). Require active>=30 and exposure>=90 or return `INCONCLUSIVE_HOLDOUT_INSUFFICIENT_EXPOSURE` without widening.
- Use identical exact DP. Success requires rate>6/45 and exact upper p<=1/20: `HISTORICAL_DISCOVERY_SELECTION_HOLDOUT_POSITIVE_PROSPECTIVE_REQUIRED`; otherwise `FAILED_NOT_REPRODUCED`.
- Positive means historical lagged crowd-metadata association only, never causality, draw-prediction support, recommendation, or Official promotion.

## Reproducibility, overfit control, and protection

- Allowed discovery is only contiguous W_PREV bands plus 1..45 enrichment inside TRAIN. Selection and untouched Holdout contain multiple-testing risk.
- No rescue, alternate band/k, second-ranked signal, period mining, or feature addition after results.
- Repeat complete deterministic calculation twice. Source, candidates, enrichment, top ten, Selection, selected signal/lock payload, Holdout activation/hits/exact p, and final verdict must match.
- Official Engine/DB, NUMBER/TRIO/PAIR/CORE, Fixed, Linked, KTS, sealed 1239, prospective log/state, existing protocols/verdicts stay unchanged. `FUTURE_LEAKAGE=0`.
