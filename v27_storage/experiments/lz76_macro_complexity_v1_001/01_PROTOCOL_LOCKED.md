# P45_LZ76_MACRO_COMPLEXITY_V1 — LOCKED PROTOCOL

- lock date: `2026-08-29 Asia/Seoul`
- research class: independent, non-Registry, non-EXP-numbered research
- Official Engine: `FROZEN`
- authoritative Registry append: `NO`
- EXP-021 assignment: `NO`
- result-dependent modification: `FORBIDDEN`

## Research question

MAIN6 역사만을 45비트 원시 흐름으로 고정 표현했을 때, 100회 롤링 LZ76 저복잡도 상태가 공정한 6/45 무작위 과정보다 더 자주 발생하고 더 강하게 시간적으로 지속되는가?

## Data lock

- rounds: exactly `1..1238`
- fields used: `MAIN6 ONLY`
- BONUS: excluded
- rounds 1239+: access/use `0`
- order: oldest round to newest; number positions `1 → 45`
- input file: `E:\P45 프로젝트\v27_storage\experiments\exp020_lagged_winner_count_regime_signal_v1_001\P45_EXP_020_OFFICIAL_FULL_HISTORY_001.csv`
- only columns `draw, main1, main2, main3, main4, main5, main6` are read. `winner_count_1st` is ignored and never analyzed.

## 45-bit encoding

For each round, create exactly 45 bits. A number position contained in MAIN6 is `1`; all others are `0`. Every round must have exactly six ones. Concatenation between rounds contains no separator, whitespace, comma, or other character.

## Rolling window

- window length: exactly `100` rounds
- bit length: exactly `4500`
- first window: rounds `1..100`
- last window: rounds `1139..1238`
- evaluated windows: `1139`
- adjacent state pairs: `1138`
- no other window length is calculated in V1.

## LZ76 parser lock

Parse left-to-right. At the current position, choose the shortest substring beginning there that has not appeared in the already processed prefix and finalize it as the next phrase. If the string ends before a new phrase can be completed, count the remaining final suffix as one phrase.

- string length: `n = 4500`
- raw diagnostic: phrase count `c(n)`
- sole primary score: `Normalized_LZ76 = c(n) * log2(n) / n`
- raw `c(n)` cannot be used for result selection.
- no external LZ package or hidden default is permitted.
- before actual data access, an independent slow reference implementation and calculator implementation must agree on at least: a repeating string, an alternating string, and a fixed-seed random string.
- implementation mismatch stop: `STOP_LZ76_IMPLEMENTATION_MISMATCH`.

## RNG lock

- API: `numpy.random.Generator`
- bit generator: `PCG64`
- threshold seed: `2026082901`
- final null seed: `2026082902`
- seed mixing, replacement, repetition, or favorable-seed selection: forbidden.

## Threshold lock

Generate `100000` independent virtual windows. Each is 100 independent fair 6-of-45 draws without replacement, encoded identically to 4500 bits. Sort Normalized_LZ76 scores ascending. Set `q` to the `20000th` value using 1-based order. State A iff `Normalized_LZ76 <= q`; ties belong to A. Actual history is not used to set q. After generation q is immutable.

## Final null lock

- independent virtual histories: `10000`
- each history: `1238` independent fair 6-of-45 draws without replacement
- rolling evaluation: identical 100-round windows and fixed q, `1139` states
- seed: `2026082902`
- per history retain only A occupancy and A/B lag-1 sample Pearson correlation.
- any null NOT_ESTIMABLE: `STOP_NULL_NOT_ESTIMABLE`; denominator is not changed.

## Primary metrics

1. Occupancy: actual A count / 1139. One-sided empirical `p1 = (count(null occupancy >= actual occupancy)+1)/10001`. Pass iff `p1 <= 0.025`.
2. Persistence: sample Pearson correlation between state positions 1..1138 and 2..1139. One-sided empirical `p2 = (count(null autocorrelation >= actual autocorrelation)+1)/10001`. Pass iff `p2 <= 0.025`.

If actual state variance is zero, persistence is NOT_ESTIMABLE and the verdict is `FAILED_NOT_SUPPORTED`.

## Verdict lock

- both p1 and p2 pass: `SUPPORTED_WITHIN_EXPERIMENT`
- otherwise: `FAILED_NOT_SUPPORTED`
- no intermediate-result rule change.

## Interpretation boundary

Even if supported, the maximum claim is: under the preregistered 45-bit MAIN6 representation and LZ76 metric, actual history showed stronger low-complexity occurrence and persistence than the fair 6/45 null.

No claim is permitted about non-randomness, manipulation, next-number prediction, strong numbers, TRIO construction, or Official P45 improvement.

## Isolation and no rescue

Do not calculate or combine Fixed, Linked, Fixed∩Linked, EXP-017 Consensus, NUMBER, TRIO, PAIR, CORE, KTS45, 3/3, exact 2/3, next-draw hit rate, number-level performance, or number subgroup results.

After V1, do not change window 100, lower 20%, compression algorithm, normalization, bit order, BONUS policy, period, direction, subgroup, or seeds. V1 result remains preserved regardless of outcome.

## Execution order

Protocol → protocol SHA/lock record → input SHA → synthetic reference/calculator agreement → input preflight → threshold 100000 → fixed q → null histories 10000 → actual once → p1/p2/verdict → save → deterministic rerun with identical input/code/seeds.

