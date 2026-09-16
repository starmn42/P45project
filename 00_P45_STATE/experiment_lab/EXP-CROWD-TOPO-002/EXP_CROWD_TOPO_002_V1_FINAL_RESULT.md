# EXP-CROWD-TOPO-002-V1 Final Result

## Judgment

- final status: `SUPPORTED_WITHIN_EXPERIMENT`
- independent reproduction: `NOT_YET`
- novelty: `NOVELTY_NOT_CONFIRMED`
- promotion candidate: `NO`
- official/DRAW effect: `NONE`

The locked historical result rejects the independent-uniform 39-column occupancy null in the direction of overdispersion. 쉽게 말하면, 2등이 되는 bonus column의 당첨게임 수가 2등+3등 전체가 39개 열에 독립·균등하게 퍼진다는 기준보다 더 들쭉날쭉했다.

이는 D1 shell 내부 crowd concentration/clustering과 일치하지만 특정 인기번호·인기조합·birthday mechanism·인과·DRAW 확률·추천 효과를 입증하지 않는다. EXP-CROWD-TOPO-001 V1의 FAILED 판정도 변경하거나 재해석하지 않는다.

## Locked evidence

- protocol version: `EXP-CROWD-TOPO-002-PROTOCOL-1.0`
- protocol SHA-256: `7d32357ff787a50e7ef67ecbcf8e38780b2886b0bf6d4ffedb1871cf35edd8c3`
- reused snapshot: `YES`
- snapshot SHA-256: `1a03abc4babec2cd64eda8c426429747352e412bc1f63e5513f7794aa980ef32`
- data range: `1~1237`
- round 1238+ used: `NO`
- D1 degree / columns / column size: `234 / 39 / 6`
- null probability: `1/39`

## Primary result

- TRAIN D: `0.757709658462612`
- TRAIN gate: `PASS`
- HOLDOUT D: `10.198417703972382`
- HOLDOUT Q: `4893.708536635931`
- MC repetitions / seed: `200000 / 2026082303`
- MC exceedances: `0`
- one-sided MC p: `0.000004999975000125`
- MC standard error: `0.000004999975000125`

## Prespecified diagnostics

- H1 D (`801~1018`): `0.962145939528479`
- H2 D (`1019~1237`): `19.392514711501015`
- half consistency: `BOTH_POSITIVE`
- positive 19-round blocks: `22 / 23`
- top 1 R removed D: `1.9686179886970279`
- top 5 R removed D: `1.0316948798049101`
- top 10 R removed D: `0.7751211403504912`
- maximum absolute z: `59.9949255651178`
- top 10 Q share: `0.8451120001824394` (`DESCRIPTIVE ONLY`)

The top-10 share shows strong concentration in a small number of rounds, but all three prespecified removal diagnostics remain positive. These diagnostics do not replace or alter the primary statistic.

## Reproduction and guards

- deterministic rerun: `PASS`
- focused tests: `7/7 PASS`
- prospective protocol changed: `NO`
- prospective signal peeking: `0`
- DRAW engine changed: `0`
- official engine: `FROZEN`
- independent implementation reproduction: `NOT_YET`

