# EXP-002 V2 봉인 검증 결과

- experiment ID: `EXP-DRAW-20260816-038-V2`
- protocol: `EXP002-V2-PROTOCOL-1.0`
- protocol hash: `eec5b8aca4d4a8b7888fb03a13f21cc2d6dcc8c3969351d993ea7b988b10b6ff`
- lock hash: `05168d0da9c9749d65a91a5293be830efc313be31e12363ca3934ef461e2bcfe`
- run ID: `e7049813-6e76-406a-9c0e-c599fc031c55`
- data boundary: `1~1235`
- status: `FAILED / B — COVERAGE_ONLY`

## Coverage

- valid NO-PICK rounds: 867
- fallback pick rounds: 412
- experimental no-pick rounds: 455
- coverage rate: 47.5201845444%

## PRIMARY와 SUPPORT

- MAIN 최소 한 TRIO 3/3: 1/412 = 0.2427184466%
- INTEGRATED 최소 한 TRIO 3/3: 4/412 = 0.9708737864%
- MAIN exact2/3 SUPPORT: A 17, B 23
- INTEGRATED exact2/3 SUPPORT: A 23, B 32

3/3과 exact2/3, MAIN과 INTEGRATED는 합산하지 않았다.

## Random/null 비교

- random MAIN primary baseline: 0.2818763766%
- random INTEGRATED primary baseline: 0.4932192028%
- MAIN Wilson 95%: 0.0428586225% ~ 1.3618735649%
- MAIN 단측 exact p: 0.6874436519
- selection-label permutation MAIN p: 0.7364726353
- selection-label permutation INTEGRATED p: 0.2221877781

MAIN primary는 random 우위를 보이지 않았다.

## 순차 안정성

- 전반부: 0/206 MAIN 3/3
- 후반부: 1/206 MAIN 3/3
- 최근100: 0/100
- 최근50: 0/50
- 최근20: 0/20 (`TEST_ONLY`)
- future leakage: 0
- hash mismatch: 0
- failed rounds: 0
- 동일 hash 10회: PASS

## 판정

Coverage는 공식 0%에서 실험 47.52%로 증가했으나 MAIN PRIMARY가 random보다 높지 않았다. 따라서 `FAILED / B`이다. SUPPORT와 INTEGRATED 성과는 MAIN 실패를 구제하지 않는다.

- FALLBACK_PROMOTION_CANDIDATE: `NO`
- ROUND1238_FORWARD_ELIGIBLE: `NO`
- ROUND1238 TRIO A/B: `NONE`
- OFFICIAL PICK: `NO`

V1 INVALID evidence는 V2 설계·성과판정에 사용하지 않았고 공식 엔진·공식 DB는 변경하지 않았다.
