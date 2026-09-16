# P45 TRIO ORBIT DIVERGENCE ATTRIBUTION V1 RESULT 001

## Final judgment

`DIVERGENCE_NOT_SUPPORTED`

직전연동이 고정 궤도에서 뺀 TRIO보다 새로 넣은 TRIO에서 exact3 성공이 2건 더 많았지만 (`7 vs 5`), 회차별 paired randomization one-sided p는 `0.386906130939`였다. 이 차이는 우연한 라벨 교환으로도 흔히 나타나며, 역사적으로 교체가 이득이었다고 판정할 근거가 없다.

## Precheck, sources, and reuse

- PRECHECK: `PASS`
- Original TRIO ORBIT V1 protocol/result/trace/output: `PASS`
- Original FINAL: `FAILED_NOT_SUPPORTED` unchanged
- Canonical latest / SHA-256: `1238 / 1160cafab32542f28b9f2e7656ec4b471d01a3a521b8b35e21dc9ae9c953cce8`
- KTS schedule SHA-256: `5f212342c6c27fca8eafbc75d20a55fc4be4ca2961a9c70c3a7af0eca26f1075` (`PASS`)
- Locked protocol SHA-256: `ed799d32979ab560ec85d1a0ba233995bb23a1dbfc1bccd8ef1834419722fac0`
- Deterministic seed / paired simulations: `17111881099788334432 / 100000`
- Existing round trace reused: `YES`; SHA-256 `bcf54e5f13bc3b3ab73eb23d936030648b7da63f9264a10bcdf715bc5ea091e7`
- KTS schedule and fixed/linked selections regenerated: `NO / NO`
- Evaluated targets: `2..1238 = 1237`

## Common-count distribution

| common count | rounds | fixed-only count/round | linked-only count/round |
|---:|---:|---:|---:|
| 0 | 1206 | 3 | 3 |
| 1 | 26 | 2 | 2 |
| 2 | 5 | 1 | 1 |
| 3 | 0 | 0 | 0 |

Every row satisfied `fixed-only = linked-only = 3-common`.

## Performance by attribution area

| area | TRIO exposures | exact3 | exact3 rate | exact3-success rounds | exact2 | exact2 rate | exact2-success rounds |
|---|---:|---:|---:|---:|---:|---:|---:|
| COMMON | 36 | 0 | 0.000000% | 0 | 1 | 2.777778% | 1 |
| FIXED_ONLY / REMOVED_BY_LINK | 3675 | 5 | 0.136054% | 5 | 160 | 4.353741% | 158 |
| LINKED_ONLY / ADDED_BY_LINK | 3675 | 7 | 0.190476% | 7 | 174 | 4.734694% | 173 |

COMMON exact2 1건을 포함하면 기존 V1 totals `fixed exact2=161`, `linked exact2=175`가 정확히 복원된다.

## Original exact3 successes by source

### Fixed 5 successes

| round | successful TRIO | source |
|---:|---|---|
| 334 | 13-15-29 | FIXED_ONLY |
| 556 | 28-30-44 | FIXED_ONLY |
| 864 | 7-13-25 | FIXED_ONLY |
| 1211 | 23-27-40 | FIXED_ONLY |
| 1229 | 13-34-37 | FIXED_ONLY |

### Linked 7 successes

| round | successful TRIO | source |
|---:|---|---|
| 74 | 6-15-18 | LINKED_ONLY |
| 167 | 27-30-36 | LINKED_ONLY |
| 625 | 3-7-20 | LINKED_ONLY |
| 902 | 19-23-36 | LINKED_ONLY |
| 1037 | 14-15-22 | LINKED_ONLY |
| 1040 | 16-26-36 | LINKED_ONLY |
| 1099 | 3-38-43 | LINKED_ONLY |

- Linked 7회 중 LINKED_ONLY 기여: `7회`
- Linked 7회 중 COMMON 기여: `0회`
- Fixed 5회 중 FIXED_ONLY 기여: `5회`
- 기존 round-level linked-only 7 / fixed-only 5 분류는 실제 성공 TRIO 출처와 정확히 일치한다. 양쪽 동시 성공과 COMMON exact3가 모두 0이기 때문이다.

## Paired randomization

- Observed linked-only exact3 / fixed-only exact3: `7 / 5`
- Difference: `+2`
- Primary one-sided p, H1 linked-only > fixed-only: `0.386906130939`
- Exact3 support two-sided p: `0.775242247578`
- Linked-only exact2 / fixed-only exact2: `174 / 160`
- Exact2 difference: `+14`
- Exact2 one-sided / two-sided p: `0.226027739723 / 0.450775492245`

These are divergence-attribution p-values only. They do not replace the original TRIO ORBIT V1 fair-null p `0.319384030798`.

## Performance by common count

| common count | rounds | fixed exact3 | linked exact3 | fixed exact2 | linked exact2 |
|---:|---:|---:|---:|---:|---:|
| 0 | 1206 | 5 | 6 | 159 | 172 |
| 1 | 26 | 0 | 1 | 1 | 2 |
| 2 | 5 | 0 | 0 | 1 | 1 |
| 3 | 0 | 0 | 0 | 0 | 0 |

This split is descriptive only and creates no common-count selection rule.

## Anchor contribution

- Anchor mapping availability: `AVAILABLE`; all `anchor_A/B/C → linked_A/B/C` membership checks passed.
- LINKED_ONLY exact3 successes with assigned anchor reappearing: `7 / 7`
- LINKED_ONLY exact3 successes with anchor missing: `0 / 7`
- In every linked-only exact3 success, the anchor plus both other TRIO members hit.
- LINKED_ONLY exact2: anchor hit `118 / 174`; anchor miss with both other members hitting `56 / 174`.

The anchor observation is attribution only. It is not a new selection rule and was not used to change the judgment.

## Protection

- FUTURE_LEAKAGE: `0`
- Existing TRIO ORBIT V1 FINAL/rules: `UNCHANGED`
- Fixed V1 / linked V1 rule changes: `0 / 0`
- KTS schedule regeneration/change: `0 / 0`
- EXP-017: `NOT_CREATED`
- Outcome-driven subgroup recommendation / linked tuning: `0 / 0`
- OFFICIAL ENGINE/gate/threshold/signature/DB and NUMBER/TRIO/PAIR/CORE changes: `0`
