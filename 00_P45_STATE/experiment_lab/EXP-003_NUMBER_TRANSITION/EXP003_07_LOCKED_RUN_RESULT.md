# EXP-003 봉인 검증 결과

- experiment: `EXP-DRAW-20260816-010-V1` (`EXP-003`)
- protocol: `EXP003-PROTOCOL-1.0`
- protocol SHA-256: `feb78db79d1dbebbfe6f41b097651aa27acdc8b7b7d7d4260e1e6645e6035329`
- data: `1~1237`, SHA-256 `b0cb865e0760060116cab5b6658eaca6d1b203d437ad7120831d5883c7f795b0`
- run_id: `14e11ba0-8760-4043-aa36-3d584a95b9cb`
- run status: `BACKTESTED_WALKFORWARD_COMPLETE`
- evaluation: `2~1237`, 1,236 transitions, 45 exact distances
- randomization: seed `202608160310`, 100,000 repetitions
- final judgment: `FAILED`
- explanation: `C` — 관찰 차이는 있으나 다중검정과 global null 이후 무작위와 구별되지 않음

## PRIMARY MAIN 결과

- Holm 통과 거리: `0`
- global maxT 통과 거리: `0`
- supported 거리: `0`
- future leakage / hash mismatch / failed / skipped: `0 / 0 / 0 / 0`

### distance 0 — 직접 재출현

- exposure / observation: `7,416 / 1,020`
- expected / observed: `13.3333% / 13.7540%`
- risk difference: `+0.4207%p`
- Wilson 95%: `12.9889% ~ 14.5567%`
- raw two-sided p: `0.265651`
- Holm p: `1.0`
- maxT p: `0.999930`

### 관찰상 극값

- 가장 큰 양의 risk difference: distance `28`, `+26.6667%p`; 단 exposure `5`, observation `2`, Holm `1.0`, maxT `0.955870`
- 가장 큰 음의 risk difference: distance `30`, `-13.3333%p`; 단 exposure `1`, observation `0`, Holm `1.0`, maxT `1.0`

극값은 매우 작은 exposure에서 발생했으며 신호나 추천 규칙으로 해석하지 않는다.

## 기간 안정성

|기간|거리 0 risk difference|Holm 통과|maxT 통과|판정|
|---|---:|---:|---:|---|
|전체|+0.4207%p|0|0|FAILED|
|전반부|+0.8522%p|0|0|NOT SUPPORTED|
|후반부|-0.0108%p|0|0|NOT SUPPORTED|
|최근100|-0.5000%p|0|0|NOT SUPPORTED|
|최근50|+1.6667%p|0|0|NOT SUPPORTED|
|최근20 TEST_ONLY|-0.8333%p|0|0|TEST ONLY / NOT SUPPORTED|

직접 재출현의 방향도 전반부·후반부·최근 구간에서 일관되지 않았다.

## 결론

R-1의 최소 절대거리 정보가 R의 MAIN 출현에 무작위와 구별되는 재현 가능한 신호를 제공한다는 가설은 이번 봉인 V1에서 지지되지 않았다. INTEGRATED는 SECONDARY이며 MAIN 실패를 구제하지 않는다. NUMBER/TRIO/PAIR/CORE, fallback 또는 추천번호에는 연결하지 않는다.

## 보존 상태

- result DB: `v27_storage/experiments/exp003/exp003_research.sqlite3`
- result DB SHA-256: `571f327cf09e0d6743dd8e23bbadae1fed46c64a12502234974282e9d222a5a0`
- result JSON: `v27_storage/experiments/exp003/exp003_locked_run_result.json`
- result JSON SHA-256: `c60168abe8623366883af6944b44e996d283c9c9435504c6fca2594c13dab3ff`
- official engine effect: `NONE`
- recommendation created: `NO`
